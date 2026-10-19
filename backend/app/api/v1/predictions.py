import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào Python path
PROJECT_ROOT = Path(__file__).resolve().parents[4]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
import logging
import os

import joblib
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from ml.training.prep_data import (
    build_feature_dataset,
    get_feature_columns,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.stock import ModelVersion, StockPrice, TechnicalIndicator
from app.schemas.prediction import (
    PredictionItem,
    PredictRequest,
    PredictResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predictions",
    tags=["ML Predictions"],
)


@router.post("/predict", response_model=PredictResponse)
def predict_stock_signals(
    payload: PredictRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> PredictResponse:
    """Chạy suy luận (Inference) bằng phiên bản mô hình ML đang hoạt động."""

    # 1. Tìm phiên bản mô hình active trong CSDL
    stmt = select(ModelVersion).where(ModelVersion.is_active == True)
    active_model_ver = db.scalars(stmt).first()

    if not active_model_ver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Không tìm thấy mô hình ML đang active. "
                "Vui lòng chạy kịch bản huấn luyện trước."
            ),
        )

    # 2. Load model và scaler artifact
    version_str = active_model_ver.version

    model_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../../../ml/models",
        )
    )

    model_path = os.path.join(
        model_dir,
        f"random_forest_{version_str}.joblib",
    )
    scaler_path = os.path.join(
        model_dir,
        f"scaler_{version_str}.joblib",
    )

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"File artifact của mô hình phiên bản "
                f"{version_str} không tồn tại."
            ),
        )

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    prediction_items: list[PredictionItem] = []

    # 3. Lặp qua danh sách cổ phiếu và dự đoán
    for sym in payload.symbols:
        symbol_upper = sym.upper()

        prices_stmt = (
            select(StockPrice)
            .where(StockPrice.symbol == symbol_upper)
            .order_by(StockPrice.date.asc())
        )
        indicators_stmt = (
            select(TechnicalIndicator)
            .where(TechnicalIndicator.symbol == symbol_upper)
            .order_by(TechnicalIndicator.date.asc())
        )

        prices = db.scalars(prices_stmt).all()
        indicators = db.scalars(indicators_stmt).all()

        if not prices or not indicators:
            continue

        price_df = pd.DataFrame(
            [
                {
                    "symbol": p.symbol,
                    "date": p.date,
                    "close": float(p.close),
                    "volume": float(p.volume),
                }
                for p in prices
            ]
        )

        indicator_df = pd.DataFrame(
            [
                {
                    "symbol": i.symbol,
                    "date": i.date,
                    "sma20": float(i.sma20 or 0),
                    "sma50": float(i.sma50 or 0),
                    "ema20": float(i.ema20 or 0),
                    "ema50": float(i.ema50 or 0),
                    "rsi14": float(i.rsi14 or 0),
                    "macd": float(i.macd or 0),
                    "macd_signal": float(i.macd_signal or 0),
                    "macd_hist": float(i.macd_hist or 0),
                    "atr14": float(i.atr14 or 0),
                }
                for i in indicators
            ]
        )

        df = build_feature_dataset(price_df, indicator_df)

        if df.empty:
            continue

        # Lấy dòng mới nhất để dự đoán
        latest_row = df.iloc[[-1]]

        features = get_feature_columns()
        X_latest = latest_row[features]
        X_scaled = scaler.transform(X_latest)

        prob_up = float(model.predict_proba(X_scaled)[0, 1])
        pred_signal = 1 if prob_up >= 0.5 else 0

        confidence = (
            prob_up if pred_signal == 1 else (1.0 - prob_up)
        )

        prediction_items.append(
            PredictionItem(
                symbol=symbol_upper,
                date=latest_row["date"].values[0],
                probability_up=round(prob_up, 4),
                predicted_signal=pred_signal,
                confidence_score=round(confidence, 4),
            )
        )

    return PredictResponse(
        status="success",
        model_version=version_str,
        predictions=prediction_items,
    )

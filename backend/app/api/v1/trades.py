import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.predictions import predict_stock_signals
from app.core.db import get_db
from app.models.stock import StockPrice, TechnicalIndicator
from app.repositories.trade_repository import TradeRepository
from app.schemas.prediction import PredictRequest
from app.schemas.trade import (
    GenerateSignalRequest,
    GenerateSignalResponse,
    SignalItem,
)
from app.services.risk_signal_service import RiskSignalService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/trades",
    tags=["Trading Signals & Plans"],
)


@router.post(
    "/generate-signals",
    response_model=GenerateSignalResponse,
)
def generate_signals_and_plans(
    payload: GenerateSignalRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> GenerateSignalResponse:
    """Tạo tín hiệu giao dịch và kế hoạch lệnh (Trade Plan) tự động."""
    trade_repo = TradeRepository(db)

    # 1. Gọi Prediction Engine lấy dự đoán từ mô hình ML
    pred_request = PredictRequest(symbols=payload.symbols)
    pred_response = predict_stock_signals(
        payload=pred_request,
        db=db,
    )

    signal_items: list[SignalItem] = []

    # 2. Xử lý từng cổ phiếu
    for pred in pred_response.predictions:
        sym = pred.symbol

        latest_price = db.scalars(
            select(StockPrice).where(StockPrice.symbol == sym).order_by(StockPrice.date.desc())
        ).first()

        latest_indicator = db.scalars(
            select(TechnicalIndicator)
            .where(TechnicalIndicator.symbol == sym)
            .order_by(TechnicalIndicator.date.desc())
        ).first()

        if not latest_price:
            continue

        close_p = float(latest_price.close)

        rsi_val = (
            float(latest_indicator.rsi14)
            if latest_indicator is not None and latest_indicator.rsi14 is not None
            else None
        )

        sma20_val = (
            float(latest_indicator.sma20)
            if latest_indicator is not None and latest_indicator.sma20 is not None
            else None
        )

        atr14_val = (
            float(latest_indicator.atr14)
            if latest_indicator is not None and latest_indicator.atr14 is not None
            else None
        )

        # 3. Sinh tín hiệu giao dịch
        sig_info = RiskSignalService.generate_signal(
            probability_up=pred.probability_up,
            rsi=rsi_val,
            close_price=close_p,
            sma20=sma20_val,
        )

        # Lưu Signal vào Supabase
        trade_repo.save_signal(
            {
                "symbol": sym,
                "timestamp": datetime.now(UTC),
                "action": sig_info["action"],
                "confidence": sig_info["confidence"],
                "reasoning": sig_info["reasoning"],
            }
        )

        plan_dict = None

        # 4. Nếu là tín hiệu BUY, tạo Trade Plan
        if sig_info["action"] == "BUY":
            plan_dict = RiskSignalService.calculate_trade_plan(
                symbol=sym,
                entry_price=close_p,
                atr14=atr14_val,
                account_risk_limit=payload.account_risk_limit,
            )

            if plan_dict is not None:
                trade_repo.save_trade_plan(plan_dict)

        signal_items.append(
            SignalItem(
                symbol=sym,
                action=sig_info["action"],
                confidence=sig_info["confidence"],
                reasoning=sig_info["reasoning"],
                trade_plan=plan_dict,
            )
        )

    return GenerateSignalResponse(
        status="success",
        signals=signal_items,
    )

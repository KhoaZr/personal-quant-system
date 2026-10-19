import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
# ============================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN VÀ IMPORT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
ENV_FILE = BACKEND_DIR / ".env"

# Cho phép import package app và ml
for path in (str(PROJECT_ROOT), str(BACKEND_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.models.stock import ModelVersion, StockPrice, TechnicalIndicator

from ml.training.prep_data import (
    build_feature_dataset,
    get_feature_columns,
)

load_dotenv(ENV_FILE)


# ============================================================
# 2. HUẤN LUYỆN VÀ ĐĂNG KÝ MÔ HÌNH
# ============================================================


def train_and_register_model() -> None:
    """Huấn luyện Random Forest và đăng ký phiên bản vào database."""
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("Lỗi: Không tìm thấy DATABASE_URL trong môi trường!")
        return

    engine = create_engine(db_url)

    try:
        with Session(engine) as db:
            # ------------------------------------------------
            # Bước 1: Lấy dữ liệu từ database
            # ------------------------------------------------
            print("1. Đang lấy dữ liệu giá và chỉ báo từ Supabase...")

            prices_stmt = select(StockPrice).order_by(
                StockPrice.symbol.asc(),
                StockPrice.date.asc(),
            )
            indicators_stmt = select(TechnicalIndicator).order_by(
                TechnicalIndicator.symbol.asc(),
                TechnicalIndicator.date.asc(),
            )

            prices = db.scalars(prices_stmt).all()
            indicators = db.scalars(indicators_stmt).all()

            if not prices or not indicators:
                print(
                    "Lỗi: CSDL chưa có giá hoặc chỉ báo. "
                    "Hãy chạy collect và calculate trước!"
                )
                return

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

            # ------------------------------------------------
            # Bước 2: Tạo feature dataset
            # ------------------------------------------------
            print("2. Tạo Feature Dataset...")

            df = build_feature_dataset(price_df, indicator_df)

            if df.empty:
                print("Lỗi: Feature Dataset rỗng!")
                return

            # Đảm bảo dữ liệu được sắp xếp theo thời gian trong từng mã
            df = df.sort_values(
                ["date", "symbol"],
                ascending=[True, True],
            ).reset_index(drop=True)

            features = get_feature_columns()

            missing_features = [
                column for column in features if column not in df.columns
            ]
            if missing_features:
                print(f"Lỗi: Thiếu các feature: {missing_features}")
                return

            X = df[features].copy()
            y = df["target"].copy()

            # ------------------------------------------------
            # Bước 3: Làm sạch dữ liệu
            # ------------------------------------------------
            print("3. Kiểm tra và làm sạch dữ liệu...")

            # Chuyển giá trị vô cực thành NaN
            X.replace([np.inf, -np.inf], np.nan, inplace=True)

            # Đảm bảo feature là dữ liệu số
            X = X.apply(pd.to_numeric, errors="coerce")

            # Loại bỏ dòng thiếu feature hoặc target
            valid_rows = X.notna().all(axis=1) & y.notna()
            removed_rows = int((~valid_rows).sum())

            X = X.loc[valid_rows].reset_index(drop=True)
            y = y.loc[valid_rows].reset_index(drop=True)

            print(f"Số dòng bị loại: {removed_rows}")
            print(f"Số dòng hợp lệ: {len(X)}")

            if len(X) < 20:
                print("Không đủ dữ liệu hợp lệ để huấn luyện!")
                return

            if y.nunique() < 2:
                print("Lỗi: Target chỉ có một lớp. Cần dữ liệu có cả nhãn 0 và 1.")
                return

            # ------------------------------------------------
            # Bước 4: Chia train/test theo thời gian
            # ------------------------------------------------
            split_idx = int(len(X) * 0.8)

            X_train = X.iloc[:split_idx]
            X_test = X.iloc[split_idx:]
            y_train = y.iloc[:split_idx]
            y_test = y.iloc[split_idx:]

            if X_train.empty or X_test.empty:
                print("Lỗi: Tập Train hoặc Test rỗng!")
                return

            if y_train.nunique() < 2:
                print(
                    "Lỗi: Tập Train chỉ có một lớp target. "
                    "Không thể huấn luyện bộ phân loại đáng tin cậy."
                )
                return

            print(f"Số mẫu Train: {len(X_train)}")
            print(f"Số mẫu Test: {len(X_test)}")

            # ------------------------------------------------
            # Bước 5: Chuẩn hóa và huấn luyện
            # ------------------------------------------------
            print("4. Huấn luyện Random Forest...")

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42,
                n_jobs=-1,
            )
            model.fit(X_train_scaled, y_train)

            # ------------------------------------------------
            # Bước 6: Đánh giá mô hình
            # ------------------------------------------------
            print("5. Đánh giá mô hình...")

            y_pred = model.predict(X_test_scaled)
            y_prob_all = model.predict_proba(X_test_scaled)

            # Tìm đúng cột xác suất ứng với nhãn 1
            class_indices = np.flatnonzero(model.classes_ == 1)

            if len(class_indices) > 0:
                y_prob = y_prob_all[:, class_indices[0]]
            else:
                y_prob = np.zeros(len(X_test))

            metrics = {
                "precision": round(
                    float(
                        precision_score(
                            y_test,
                            y_pred,
                            zero_division=0,
                        )
                    ),
                    4,
                ),
                "recall": round(
                    float(
                        recall_score(
                            y_test,
                            y_pred,
                            zero_division=0,
                        )
                    ),
                    4,
                ),
                "f1": round(
                    float(
                        f1_score(
                            y_test,
                            y_pred,
                            zero_division=0,
                        )
                    ),
                    4,
                ),
                "auc": (
                    round(float(roc_auc_score(y_test, y_prob)), 4)
                    if y_test.nunique() == 2
                    else 0.5
                ),
            }

            print("Chỉ số đánh giá mô hình:", metrics)

            # ------------------------------------------------
            # Bước 7: Lưu model và scaler
            # ------------------------------------------------
            print("6. Lưu model và scaler...")

            version_str = f"v{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

            MODEL_DIR.mkdir(parents=True, exist_ok=True)

            artifact_path = MODEL_DIR / (f"random_forest_{version_str}.joblib")
            scaler_path = MODEL_DIR / (f"scaler_{version_str}.joblib")

            joblib.dump(model, artifact_path)
            joblib.dump(scaler, scaler_path)

            # ------------------------------------------------
            # Bước 8: Đăng ký phiên bản model trong database
            # ------------------------------------------------
            print("7. Đăng ký phiên bản mô hình vào Supabase...")

            # Dùng truy vấn SQLAlchemy để vô hiệu hóa model cũ
            db.query(ModelVersion).filter(ModelVersion.is_active.is_(True)).update(
                {"is_active": False},
                synchronize_session=False,
            )

            model_version = ModelVersion(
                model_name="RandomForest_Classifier",
                version=version_str,
                algorithm="RandomForest",
                metrics=metrics,
                parameters={
                    "n_estimators": 100,
                    "max_depth": 5,
                    "horizon": 5,
                    "features": features,
                    "scaler": "StandardScaler",
                    "train_samples": len(X_train),
                    "test_samples": len(X_test),
                },
                is_active=True,
            )

            db.add(model_version)
            db.commit()

            print("Huấn luyện và đăng ký mô hình thành công!")
            print(f"Phiên bản active: {version_str}")
            print(f"Model: {artifact_path}")
            print(f"Scaler: {scaler_path}")

    except Exception:
        print("Lỗi trong quá trình huấn luyện hoặc đăng ký mô hình.")
        logger.exception("Training pipeline failed")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    train_and_register_model()

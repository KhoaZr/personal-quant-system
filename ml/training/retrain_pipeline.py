
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    f1_score,
    precision_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# ============================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
MODEL_DIR = ROOT_DIR / "ml" / "models"

sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from app.models.stock import (  # noqa: E402
    ModelVersion,
    StockPrice,
    TechnicalIndicator,
)
from ml.training.prep_data import (  # noqa: E402
    build_feature_dataset,
    get_feature_columns,
)

load_dotenv(BACKEND_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# Cấu hình huấn luyện
TEST_RATIO = 0.2
MIN_DATASET_SIZE = 50
RANDOM_STATE = 42
N_ESTIMATORS = 150
MAX_DEPTH = 7


# ============================================================
# 2. ĐỌC DỮ LIỆU TỪ DATABASE
# ============================================================

def load_historical_data(
    db: Session,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Đọc giá lịch sử và các chỉ báo kỹ thuật."""

    prices = db.scalars(
        select(StockPrice).order_by(
            StockPrice.date.asc(),
            StockPrice.symbol.asc(),
        )
    ).all()

    indicators = db.scalars(
        select(TechnicalIndicator).order_by(
            TechnicalIndicator.date.asc(),
            TechnicalIndicator.symbol.asc(),
        )
    ).all()

    price_df = pd.DataFrame(
        [
            {
                "symbol": price.symbol,
                "date": price.date,
                "close": price.close,
                "volume": price.volume,
            }
            for price in prices
        ]
    )

    indicator_df = pd.DataFrame(
        [
            {
                "symbol": indicator.symbol,
                "date": indicator.date,
                "sma20": indicator.sma20,
                "sma50": indicator.sma50,
                "ema20": indicator.ema20,
                "ema50": indicator.ema50,
                "rsi14": indicator.rsi14,
                "macd": indicator.macd,
                "macd_signal": indicator.macd_signal,
                "macd_hist": indicator.macd_hist,
                "atr14": indicator.atr14,
            }
            for indicator in indicators
        ]
    )

    if price_df.empty:
        raise ValueError("Database không có dữ liệu StockPrice.")

    if indicator_df.empty:
        raise ValueError(
            "Database không có dữ liệu TechnicalIndicator."
        )

    return price_df, indicator_df


# ============================================================
# 3. LÀM SẠCH DATASET
# ============================================================

def clean_feature_dataset(
    df: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:
    """Làm sạch feature và target trước khi chia tập dữ liệu."""

    required_columns = features + ["target"]
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset thiếu các cột bắt buộc: {missing_columns}"
        )

    df = df.copy()

    # Chuyển feature và target sang kiểu số.
    for column in required_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Chuyển infinity thành NaN để xử lý ở bước tiếp theo.
    df[required_columns] = df[required_columns].replace(
        [np.inf, -np.inf],
        np.nan,
    )

    # Không được tự điền target vì sẽ làm sai nhãn huấn luyện.
    before = len(df)

    df = df.dropna(subset=["target"]).copy()

    # Bài toán phân loại nhị phân: chỉ nhận target 0 hoặc 1.
    df = df[df["target"].isin([0, 1])].copy()

    removed_targets = before - len(df)

    # Kiểm tra các feature có infinity trước khi chuyển đổi.
    print("\nKiểm tra dữ liệu đầu vào:")

    if len(df) > 0:
        missing_counts = df[features].isna().sum()
        missing_counts = missing_counts[
            missing_counts > 0
        ]

        if missing_counts.empty:
            print("  Không còn feature bị thiếu.")
        else:
            print("  Feature bị thiếu:")
            print(missing_counts.to_string())

    print(
        "  Số hàng bị loại do target thiếu/không hợp lệ:",
        removed_targets,
    )

    if df.empty:
        raise ValueError(
            "Không còn mẫu hợp lệ sau khi làm sạch target."
        )

    # Kiểm tra giá trị quá lớn để cảnh báo, không âm thầm
    # cắt ngưỡng hoặc thay đổi ý nghĩa của dữ liệu.
    max_abs = df[features].abs().max()

    print("\nGiá trị tuyệt đối lớn nhất theo feature:")
    print(max_abs.sort_values(ascending=False).head(10))

    return df


# ============================================================
# 4. HUẤN LUYỆN, ĐÁNH GIÁ VÀ DEPLOY CANDIDATE
# ============================================================

def retrain_and_evaluate_candidate() -> None:
    """Huấn luyện Candidate và chỉ deploy khi đạt điều kiện."""

    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        logger.error("Không tìm thấy DATABASE_URL trong backend/.env")
        return

    engine = create_engine(db_url, pool_pre_ping=True)

    try:
        with Session(engine) as db:
            # ------------------------------------------------
            # Bước 1: Lấy mô hình đang active
            # ------------------------------------------------
            print(
                "\n1. Đọc dữ liệu lịch sử từ Supabase..."
            )

            active_models = db.scalars(
                select(ModelVersion).where(
                    ModelVersion.is_active.is_(True)
                )
            ).all()

            if len(active_models) > 1:
                raise RuntimeError(
                    "Database có nhiều hơn một mô hình active. "
                    "Cần xử lý trạng thái mô hình trước khi retrain."
                )

            active_model = (
                active_models[0] if active_models else None
            )

            current_f1 = (
                float(active_model.metrics.get("f1", 0.0))
                if active_model and active_model.metrics
                else 0.0
            )

            active_version = (
                active_model.version
                if active_model
                else "None"
            )

            print(
                f"Mô hình active hiện tại: {active_version} "
                f"| Current F1: {current_f1:.4f}"
            )

            # -----------------------------------------------
            # Bước 2: Đọc và tạo feature dataset
            # -----------------------------------------------
            price_df, indicator_df = load_historical_data(db)

            df = build_feature_dataset(
                price_df,
                indicator_df,
            )

            if df.empty:
                logger.error(
                    "build_feature_dataset trả về dataset rỗng."
                )
                return

            features = list(get_feature_columns())

            df = clean_feature_dataset(df, features)

            if len(df) < MIN_DATASET_SIZE:
                logger.error(
                    "Chỉ còn %s mẫu hợp lệ; cần ít nhất %s mẫu.",
                    len(df),
                    MIN_DATASET_SIZE,
                )
                return

            # Giữ thứ tự thời gian nếu dataset có cột date.
            if "date" in df.columns:
                df = df.sort_values(
                    ["date", "symbol"]
                    if "symbol" in df.columns
                    else ["date"]
                ).reset_index(drop=True)
            else:
                logger.warning(
                    "Dataset không có cột date. "
                    "Giữ nguyên thứ tự do build_feature_dataset tạo ra."
                )

            X = df[features]
            y = df["target"].astype(int)

            # -----------------------------------------------
            # Bước 3: Chia Train / Out-of-Sample theo thời gian
            # -----------------------------------------------
            split_idx = int(len(df) * (1 - TEST_RATIO))

            X_train = X.iloc[:split_idx]
            X_oos = X.iloc[split_idx:]

            y_train = y.iloc[:split_idx]
            y_oos = y.iloc[split_idx:]

            if X_train.empty or X_oos.empty:
                logger.error(
                    "Không đủ dữ liệu để chia Train/OOS."
                )
                return

            if y_train.nunique() < 2:
                logger.error(
                    "Train cần có ít nhất hai lớp nhãn."
                )
                return

            print(f"Tổng số mẫu: {len(df)}")
            print(f"Train: {len(X_train)} mẫu")
            print(f"OOS: {len(X_oos)} mẫu")
            print(f"Train label distribution:\n{y_train.value_counts()}")
            print(f"OOS label distribution:\n{y_oos.value_counts()}")

            # -----------------------------------------------
            # Bước 4: Điền feature thiếu và chuẩn hóa
            # -----------------------------------------------
            print("\n2. Huấn luyện Candidate mới...")

            # Imputer chỉ fit trên train, tránh rò rỉ dữ liệu OOS.
            imputer = SimpleImputer(
                strategy="median",
                keep_empty_features=True,
            )

            X_train_imputed = imputer.fit_transform(X_train)
            X_oos_imputed = imputer.transform(X_oos)

            # Kiểm tra lại dữ liệu sau khi impute.
            if not np.isfinite(X_train_imputed).all():
                raise ValueError(
                    "Train vẫn có NaN/inf sau khi impute."
                )

            if not np.isfinite(X_oos_imputed).all():
                raise ValueError(
                    "OOS vẫn có NaN/inf sau khi impute."
                )

            scaler = StandardScaler()

            X_train_scaled = scaler.fit_transform(
                X_train_imputed
            )

            X_oos_scaled = scaler.transform(
                X_oos_imputed
            )

            # -----------------------------------------------
            # Bước 5: Huấn luyện Random Forest
            # -----------------------------------------------
            candidate_model = RandomForestClassifier(
                n_estimators=N_ESTIMATORS,
                max_depth=MAX_DEPTH,
                random_state=RANDOM_STATE,
                class_weight="balanced",
                n_jobs=-1,
            )

            candidate_model.fit(
                X_train_scaled,
                y_train,
            )

            # -----------------------------------------------
            # Bước 6: Đánh giá trên OOS
            # -----------------------------------------------
            y_pred_oos = candidate_model.predict(
                X_oos_scaled
            )

            y_prob_oos = candidate_model.predict_proba(
                X_oos_scaled
            )[:, 1]

            candidate_f1 = float(
                f1_score(
                    y_oos,
                    y_pred_oos,
                    zero_division=0,
                )
            )

            candidate_precision = float(
                precision_score(
                    y_oos,
                    y_pred_oos,
                    zero_division=0,
                )
            )

            candidate_auc = (
                float(roc_auc_score(y_oos, y_prob_oos))
                if y_oos.nunique() == 2
                else None
            )

            candidate_metrics: dict[str, Any] = {
                "precision": round(candidate_precision, 4),
                "f1": round(candidate_f1, 4),
                "auc": (
                    round(candidate_auc, 4)
                    if candidate_auc is not None
                    else None
                ),
                "train_samples": int(len(X_train)),
                "oos_samples": int(len(X_oos)),
                "features": features,
            }

            print("\n3. Kết quả đánh giá Candidate:")
            print(f"Precision: {candidate_metrics['precision']}")
            print(f"F1:        {candidate_metrics['f1']}")
            print(f"AUC:       {candidate_metrics['auc']}")

            # Không deploy nếu OOS không có cả hai lớp.
            if y_oos.nunique() < 2:
                logger.warning(
                    "OOS chỉ có một lớp nhãn; "
                    "không deploy Candidate vì đánh giá chưa đủ tin cậy."
                )
                return

            # -----------------------------------------------
            # Bước 7: So sánh với mô hình active
            # -----------------------------------------------
            if candidate_f1 <= current_f1:
                print(
                    "\nCandidate KHÔNG vượt qua điều kiện F1: "
                    f"{candidate_f1:.4f} <= {current_f1:.4f}. "
                    "Giữ nguyên mô hình active."
                )
                return

            print(
                "\nCandidate có F1 cao hơn mô hình active. "
                "Đang chuẩn bị deploy..."
            )

            # -----------------------------------------------
            # Bước 8: Lưu artifact của Candidate
            # -----------------------------------------------
            version_str = (
                f"v{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
            )

            MODEL_DIR.mkdir(parents=True, exist_ok=True)

            model_path = MODEL_DIR / (
                f"random_forest_{version_str}.joblib"
            )
            scaler_path = MODEL_DIR / (
                f"scaler_{version_str}.joblib"
            )
            imputer_path = MODEL_DIR / (
                f"imputer_{version_str}.joblib"
            )

            joblib.dump(candidate_model, model_path)
            joblib.dump(scaler, scaler_path)
            joblib.dump(imputer, imputer_path)

            # -----------------------------------------------
            # Bước 9: Cập nhật active trong transaction
            # -----------------------------------------------
            try:
                if active_model is not None:
                    active_model.is_active = False

                new_version = ModelVersion(
                    model_name="RandomForest_Candidate",
                    version=version_str,
                    algorithm="RandomForest",
                    metrics=candidate_metrics,
                    parameters={
                        "n_estimators": N_ESTIMATORS,
                        "max_depth": MAX_DEPTH,
                        "random_state": RANDOM_STATE,
                        "class_weight": "balanced",
                        "test_ratio": TEST_RATIO,
                        "imputer": "median",
                        "scaler": "StandardScaler",
                    },
                    is_active=True,
                )

                db.add(new_version)
                db.commit()

            except Exception:
                db.rollback()

                # Xóa artifact mới nếu cập nhật database thất bại.
                for path in (
                    model_path,
                    scaler_path,
                    imputer_path,
                ):
                    path.unlink(missing_ok=True)

                raise

            print(
                "\nDEPLOY THÀNH CÔNG!"
                f"\nVersion: {version_str}"
                f"\nModel:   {model_path}"
                f"\nScaler:  {scaler_path}"
                f"\nImputer: {imputer_path}"
            )

    except Exception:
        logger.exception(
            "Retraining thất bại. Mô hình active không được "
            "cố ý thay đổi nếu quá trình huấn luyện hoặc đánh giá lỗi."
        )
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    retrain_and_evaluate_candidate()

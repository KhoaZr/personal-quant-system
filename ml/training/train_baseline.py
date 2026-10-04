import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


# ============================================================
# CONFIG
# ============================================================

TRAIN_PATH = "data/clean/train.csv"
VALIDATION_PATH = "data/clean/validation.csv"

FEATURE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "sma20",
    "sma50",
    "ema20",
    "ema50",
    "rsi14",
    "macd",
    "macd_signal",
    "macd_hist",
    "atr14",
    "obv",
    "bollinger_upper",
    "bollinger_middle",
    "bollinger_lower",
]

TARGET_COLUMN = "target"


# ============================================================
# 1. LOAD DATA
# ============================================================

def load_data():
    print("[1/5] Đọc dữ liệu...")

    train_df = pd.read_csv(TRAIN_PATH)
    validation_df = pd.read_csv(VALIDATION_PATH)

    print(f"Train: {len(train_df):,} dòng")
    print(f"Validation: {len(validation_df):,} dòng")

    return train_df, validation_df


# ============================================================
# 2. PREPARE X / y
# ============================================================

def prepare_features(train_df, validation_df):
    print("\n[2/5] Chuẩn bị Features / Target...")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]

    X_validation = validation_df[FEATURE_COLUMNS]
    y_validation = validation_df[TARGET_COLUMN]

    print(f"Số features: {len(FEATURE_COLUMNS)}")
    print(f"X_train shape: {X_train.shape}")
    print(f"y_train shape: {y_train.shape}")

    return X_train, y_train, X_validation, y_validation


# ============================================================
# 3. SCALE DATA
# ============================================================

def scale_features(X_train, X_validation):
    print("\n[3/5] Chuẩn hóa dữ liệu...")

    scaler = StandardScaler()

    # CHỈ fit trên TRAIN
    X_train_scaled = scaler.fit_transform(X_train)

    # Validation chỉ transform
    X_validation_scaled = scaler.transform(X_validation)

    print("StandardScaler đã được fit trên Train.")

    return X_train_scaled, X_validation_scaled, scaler


# ============================================================
# 4. TRAIN MODEL
# ============================================================

def train_model(X_train, y_train):
    print("\n[4/5] Huấn luyện Logistic Regression...")

    model = LogisticRegression(
        max_iter=1000,
        random_state=42
    )

    model.fit(X_train, y_train)

    print("Huấn luyện hoàn tất.")

    return model


# ============================================================
# 5. EVALUATE
# ============================================================

def evaluate_model(model, X_validation, y_validation):
    print("\n[5/5] Đánh giá model...")

    y_pred = model.predict(X_validation)

    y_probability = model.predict_proba(X_validation)[:, 1]

    accuracy = accuracy_score(y_validation, y_pred)
    precision = precision_score(y_validation, y_pred)
    recall = recall_score(y_validation, y_pred)
    f1 = f1_score(y_validation, y_pred)
    roc_auc = roc_auc_score(y_validation, y_probability)

    cm = confusion_matrix(y_validation, y_pred)

    print("\n===== MODEL EVALUATION =====")

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(cm)


# ============================================================
# MAIN
# ============================================================

def main():

    train_df, validation_df = load_data()

    (
        X_train,
        y_train,
        X_validation,
        y_validation
    ) = prepare_features(
        train_df,
        validation_df
    )

    (
        X_train_scaled,
        X_validation_scaled,
        scaler
    ) = scale_features(
        X_train,
        X_validation
    )

    model = train_model(
        X_train_scaled,
        y_train
    )

    evaluate_model(
        model,
        X_validation_scaled,
        y_validation
    )


if __name__ == "__main__":
    main()
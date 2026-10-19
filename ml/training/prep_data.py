
import pandas as pd


def build_feature_dataset(
    price_df: pd.DataFrame,
    indicator_df: pd.DataFrame,
    target_horizon: int = 5,
) -> pd.DataFrame:
    """Kết hợp giá và chỉ báo kỹ thuật, tạo thêm Features và Target Label cho ML."""
    if price_df.empty or indicator_df.empty:
        return pd.DataFrame()

    # 1. Merge giá và chỉ báo theo symbol và date
    df = pd.merge(
        price_df,
        indicator_df,
        on=["symbol", "date"],
        how="inner",
    )
    df.sort_values(by=["symbol", "date"], inplace=True)

    # 2. Tạo các đặc trưng bổ sung (Feature Engineering)
    df["return_1d"] = df.groupby("symbol")["close"].pct_change(1)
    df["return_5d"] = df.groupby("symbol")["close"].pct_change(5)
    df["return_20d"] = df.groupby("symbol")["close"].pct_change(20)

    # Tỷ lệ giá so với các đường trung bình động
    df["price_to_sma20"] = df["close"] / df["sma20"]
    df["price_to_sma50"] = df["close"] / df["sma50"]

    # 3. Tạo Target Label
    # Target = 1 nếu giá sau N phiên > giá hiện tại, ngược lại = 0
    df["future_close"] = (
        df.groupby("symbol")["close"].shift(-target_horizon)
    )
    df["target"] = (df["future_close"] > df["close"]).astype(int)

    # 4. Loại bỏ các dòng bị khuyết do pct_change và shift
    df.dropna(
        subset=[
            "return_20d",
            "sma50",
            "rsi14",
            "macd",
            "future_close",
        ],
        inplace=True,
    )

    return df


def get_feature_columns() -> list[str]:
    """Danh sách tên cột đầu vào cho mô hình Machine Learning."""
    return [
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
        "price_to_sma20",
        "price_to_sma50",
        "return_1d",
        "return_5d",
        "return_20d",
    ]

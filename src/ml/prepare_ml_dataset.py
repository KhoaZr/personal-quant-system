import pandas as pd

from src.database.db import engine


# ============================================================
# Feature columns
# ============================================================

FEATURE_COLUMNS = [
    # Price / Volume
    "open",
    "high",
    "low",
    "close",
    "volume",

    # SMA
    "sma20",
    "sma50",

    # EMA
    "ema20",
    "ema50",

    # RSI
    "rsi14",

    # MACD
    "macd",
    "macd_signal",
    "macd_hist",

    # ATR
    "atr14",

    # OBV
    "obv",

    # Bollinger Bands
    "bollinger_upper",
    "bollinger_middle",
    "bollinger_lower",
]


# ============================================================
# Load data from PostgreSQL
# ============================================================

def load_ml_data() -> pd.DataFrame:
    """
    Đọc stock_prices và technical_indicators
    từ PostgreSQL và kết hợp thành ML dataset.
    """

    query = """
        SELECT
            sp.symbol,
            sp.date,

            sp.open,
            sp.high,
            sp.low,
            sp.close,
            sp.volume,

            ti.sma20,
            ti.sma50,
            ti.ema20,
            ti.ema50,
            ti.rsi14,
            ti.macd,
            ti.macd_signal,
            ti.macd_hist,
            ti.atr14,
            ti.obv,
            ti.bollinger_upper,
            ti.bollinger_middle,
            ti.bollinger_lower

        FROM stock_prices sp

        INNER JOIN technical_indicators ti
            ON sp.symbol = ti.symbol
            AND sp.date = ti.date

        ORDER BY
            sp.symbol,
            sp.date;
    """

    df = pd.read_sql_query(
        query,
        engine
    )

    return df


# ============================================================
# Create target
# ============================================================

def create_target(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Tạo target dự đoán giá ngày tiếp theo tăng hay giảm.

    target:
        1 = giá ngày mai > giá hôm nay
        0 = giá ngày mai <= giá hôm nay
        NaN = không có dữ liệu ngày tiếp theo
    """

    df = df.copy()

    # --------------------------------------------------------
    # Giá đóng cửa của ngày tiếp theo
    # --------------------------------------------------------

    df["future_close"] = (
        df.groupby("symbol")["close"]
        .shift(-1)
    )

    # --------------------------------------------------------
    # Tạo target
    # --------------------------------------------------------

    df["target"] = (
        df["future_close"] > df["close"]
    ).

    # Dòng cuối của mỗi symbol không có ngày tiếp theo
    df.loc[
        df["future_close"].isna(),
        "target"
    ] = pd.NA

    return df

# ============================================================
# Remove invalid rows
# ============================================================

def clean_ml_data(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Xử lý các dòng không đủ dữ liệu cho ML.
    """

    df = df.copy()

    columns_for_ml = [
        "symbol",
        "date",
        *FEATURE_COLUMNS,
        "target"
    ]

    # Chỉ giữ các columns cần thiết
    df = df[columns_for_ml]

    # Loại bỏ NaN
    before = len(df)

    df = df.dropna(
        subset=FEATURE_COLUMNS + ["target"]
    )

    after = len(df)

    print(
        f"\nĐã loại bỏ {before - after:,} "
        "dòng chứa NaN."
    )

    return df


# ============================================================
# Validate ML dataset
# ============================================================

def validate_ml_dataset(
    df: pd.DataFrame
) -> None:
    """
    Kiểm tra dataset trước khi đưa vào ML.
    """

    print(
        "\n===== KIỂM TRA ML DATASET ====="
    )

    # --------------------------------------------------------
    # 1. Số dòng
    # --------------------------------------------------------

    print(
        f"Số dòng: {len(df):,}"
    )

    # --------------------------------------------------------
    # 2. Số symbol
    # --------------------------------------------------------

    print(
        f"Số symbol: {df['symbol'].nunique()}"
    )

    # --------------------------------------------------------
    # 3. Thời gian
    # --------------------------------------------------------

    print(
        f"Ngày bắt đầu: {df['date'].min()}"
    )

    print(
        f"Ngày kết thúc: {df['date'].max()}"
    )

    # --------------------------------------------------------
    # 4. Missing values
    # --------------------------------------------------------

    print("\nMissing values:")

    print(
        df.isna().sum()
    )

    # --------------------------------------------------------
    # 5. Duplicate
    # --------------------------------------------------------

    duplicate_count = (
        df
        .duplicated(
            subset=["symbol", "date"]
        )
        .sum()
    )

    print(
        f"\nDuplicate (symbol, date): "
        f"{duplicate_count}"
    )

    if duplicate_count > 0:
        raise ValueError(
            "Phát hiện duplicate symbol + date."
        )

    # --------------------------------------------------------
    # 6. Target distribution
    # --------------------------------------------------------

    print(
        "\nTarget distribution:"
    )

    print(
        df["target"]
        .value_counts()
        .sort_index()
    )

    print(
        "\nTarget percentage:"
    )

    print(
        df["target"]
        .value_counts(
            normalize=True
        )
        .sort_index()
        .mul(100)
        .round(2)
    )

    print(
        "\nKiểm tra ML dataset hoàn tất."
    )


# ============================================================
# Save dataset
# ============================================================

def save_ml_dataset(
    df: pd.DataFrame
) -> None:
    """
    Lưu ML dataset thành CSV.
    """

    output_path = (
        "data/clean/ml_dataset.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nĐã lưu ML dataset:"
        f" {output_path}"
    )


# ============================================================
# Main
# ============================================================

def main():

    print(
        "========================================"
    )

    print(
        "       PREPARE ML DATASET"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # 1. Load data
    # --------------------------------------------------------

    print(
        "\n[1/5] Đọc dữ liệu từ PostgreSQL..."
    )

    df = load_ml_data()

    if df.empty:
        raise ValueError(
            "Không có dữ liệu để tạo ML dataset."
        )

    print(
        f"Đã đọc {len(df):,} dòng."
    )

    # --------------------------------------------------------
    # 2. Create target
    # --------------------------------------------------------

    print(
        "\n[2/5] Tạo target..."
    )

    df = create_target(
        df
    )

    print(
        "Đã tạo target."
    )

    # --------------------------------------------------------
    # 3. Clean data
    # --------------------------------------------------------

    print(
        "\n[3/5] Làm sạch ML dataset..."
    )

    df = clean_ml_data(
        df
    )

    # --------------------------------------------------------
    # 4. Validate
    # --------------------------------------------------------

    print(
        "\n[4/5] Kiểm tra ML dataset..."
    )

    validate_ml_dataset(
        df
    )

    # --------------------------------------------------------
    # 5. Save
    # --------------------------------------------------------

    print(
        "\n[5/5] Lưu ML dataset..."
    )

    save_ml_dataset(
        df
    )

    print(
        "\n========================================"
    )

    print(
        "              HOÀN TẤT"
    )

    print(
        "========================================"
    )


if __name__ == "__main__":
    main()
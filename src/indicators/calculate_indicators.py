import pandas as pd

from src.database.db import engine
from src.indicators.technical_indicators import (
    calculate_all_indicators
)


# ============================================================
# Load stock prices from PostgreSQL
# ============================================================

def load_stock_prices() -> pd.DataFrame:
    """
    Đọc dữ liệu OHLCV từ bảng stock_prices.
    """

    query = """
        SELECT
            symbol,
            date,
            open,
            high,
            low,
            close,
            volume
        FROM stock_prices
        ORDER BY symbol, date;
    """

    df = pd.read_sql_query(
        query,
        engine
    )

    return df


# ============================================================
# Calculate indicators for all symbols
# ============================================================

def calculate_indicators_for_all_symbols(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Tính technical indicators cho từng mã chứng khoán.

    Mỗi symbol được tính độc lập để tránh rolling window
    và các phép tính khác chạy xuyên giữa các mã.
    """

    results = []

    symbols = df["symbol"].dropna().unique()

    print(
        f"Tìm thấy {len(symbols)} mã chứng khoán."
    )

    for symbol in symbols:

        print(
            f"Đang tính indicators cho {symbol}..."
        )

        # Lấy dữ liệu của một symbol
        symbol_df = df[
            df["symbol"] == symbol
        ].copy()

        # Sắp xếp theo ngày
        symbol_df = (
            symbol_df
            .sort_values("date")
            .reset_index(drop=True)
        )

        # Tính toàn bộ indicators
        symbol_df = calculate_all_indicators(
            symbol_df
        )

        results.append(symbol_df)

    if not results:
        raise ValueError(
            "Không có dữ liệu để tính indicators."
        )

    # Ghép tất cả symbol lại
    result_df = pd.concat(
        results,
        ignore_index=True
    )

    # Sắp xếp lại
    result_df = (
        result_df
        .sort_values(
            ["symbol", "date"]
        )
        .reset_index(drop=True)
    )

    return result_df


# ============================================================
# Validate result
# ============================================================

def validate_indicator_result(
    df: pd.DataFrame
) -> None:
    """
    Kiểm tra kết quả tính indicators.
    """

    indicator_columns = [
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
        "bollinger_lower"
    ]

    print("\n===== KIỂM TRA KẾT QUẢ =====")

    # --------------------------------------------------------
    # 1. Kiểm tra số dòng
    # --------------------------------------------------------

    print(
        f"Số dòng: {len(df):,}"
    )

    # --------------------------------------------------------
    # 2. Kiểm tra số symbol
    # --------------------------------------------------------

    print(
        f"Số symbol: {df['symbol'].nunique()}"
    )

    # --------------------------------------------------------
    # 3. Kiểm tra khoảng thời gian
    # --------------------------------------------------------

    print(
        f"Ngày bắt đầu: {df['date'].min()}"
    )

    print(
        f"Ngày kết thúc: {df['date'].max()}"
    )

    # --------------------------------------------------------
    # 4. Kiểm tra NaN
    # --------------------------------------------------------

    print("\nSố lượng NaN:")

    print(
        df[indicator_columns]
        .isna()
        .sum()
    )

    # --------------------------------------------------------
    # 5. Kiểm tra RSI
    # --------------------------------------------------------

    valid_rsi = df["rsi14"].dropna()

    if not valid_rsi.empty:

        print(
            "\nRSI14:"
        )

        print(
            f"Min: {valid_rsi.min():.4f}"
        )

        print(
            f"Max: {valid_rsi.max():.4f}"
        )

        if (
            valid_rsi.min() < 0
            or valid_rsi.max() > 100
        ):
            raise ValueError(
                "RSI14 nằm ngoài khoảng 0-100."
            )

    # --------------------------------------------------------
    # 6. Kiểm tra ATR
    # --------------------------------------------------------

    valid_atr = df["atr14"].dropna()

    if not valid_atr.empty:

        if (valid_atr < 0).any():
            raise ValueError(
                "ATR14 không được âm."
            )

        print(
            "\nATR14 hợp lệ."
        )

    # --------------------------------------------------------
    # 7. Kiểm tra duplicate symbol + date
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

    print(
        "\nKiểm tra hoàn tất."
    )


# ============================================================
# Display sample
# ============================================================

def display_sample(
    df: pd.DataFrame,
    symbol: str | None = None,
    rows: int = 10
) -> None:
    """
    Hiển thị một số dòng kết quả để kiểm tra.
    """

    columns = [
        "symbol",
        "date",
        "close",
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
        "bollinger_lower"
    ]

    sample = df

    if symbol is not None:
        sample = sample[
            sample["symbol"] == symbol
        ]

    print(
        "\n===== SAMPLE KẾT QUẢ ====="
    )

    print(
        sample[columns]
        .tail(rows)
        .to_string(index=False)
    )


# ============================================================
# Main
# ============================================================

def main():

    print(
        "===== TECHNICAL INDICATORS ====="
    )

    # --------------------------------------------------------
    # 1. Đọc stock_prices
    # --------------------------------------------------------

    print(
        "\n[1/4] Đang đọc stock_prices..."
    )

    df = load_stock_prices()

    if df.empty:
        raise ValueError(
            "Bảng stock_prices không có dữ liệu."
        )

    print(
        f"Đã đọc {len(df):,} dòng."
    )

    # --------------------------------------------------------
    # 2. Tính indicators
    # --------------------------------------------------------

    print(
        "\n[2/4] Đang tính technical indicators..."
    )

    result_df = (
        calculate_indicators_for_all_symbols(df)
    )

    print(
        "\nĐã tính xong tất cả indicators."
    )

    # --------------------------------------------------------
    # 3. Validate
    # --------------------------------------------------------

    print(
        "\n[3/4] Đang kiểm tra kết quả..."
    )

    validate_indicator_result(
        result_df
    )

    # --------------------------------------------------------
    # 4. Hiển thị kết quả
    # --------------------------------------------------------

    print(
        "\n[4/4] Hiển thị kết quả..."
    )

    # Nếu muốn kiểm tra riêng FPT:
    display_sample(
        result_df,
        symbol="FPT.VN",
        rows=10
    )

    print(
        "\nHoàn tất."
    )

    return result_df


if __name__ == "__main__":
    main()
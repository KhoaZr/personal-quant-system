import numpy as np
import pandas as pd
from sqlalchemy import text

from src.database.db import engine



from src.indicators.calculate_indicators import (
    load_stock_prices,
    calculate_indicators_for_all_symbols,
    validate_indicator_result
)

# ===================================================
# Column to save
# ===================================================

INDICATOR_COLUMNS = [
    "symbol",
    "date",
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


# ==========================================================
# Save indicators to PostgreSQL
# ==========================================================


def save_indicators(df: pd.DataFrame) -> None:
    """
    Lưu technical indicators vào bảng technical_indicators.

    Dữ liệu cũ trong technical_indicators sẽ được xóa
    và thay thế bằng dữ liệu mới.

    Toàn bộ quá trình nằm trong một transaction.
    Nếu insert thất bại, dữ liệu cũ sẽ được rollback.
    """
    print("\n===== LƯU TECHNICAL INDICATORS =====")

    # --------------------------------------------------------
    # 1. Chọn các columns cần lưu
    # --------------------------------------------------------

    save_df = df[INDICATOR_COLUMNS].copy()

    # --------------------------------------------------------
    # 2. Đảm bảo kiểu dữ liệu
    # --------------------------------------------------------

    save_df["symbol"] = save_df["symbol"].astype(str)

    save_df["date"] = pd.to_datetime(
        save_df["date"]
    ).dt.date

    # --------------------------------------------------------
    # 3. Chuyển NaN thành None
    # --------------------------------------------------------

    # PostgreSQL sẽ lưu None thành NULL
    # thay vì lưu NaN.
    save_df = save_df.replace(
        {np.nan: None}
    )

    # --------------------------------------------------------
    # 4. Kiểm tra duplicate
    # --------------------------------------------------------

    duplicate_count = (
        save_df
        .duplicated(
            subset=["symbol", "date"]
        )
        .sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"Phát hiện {duplicate_count} "
            "duplicate (symbol, date)."
        )

    print(
        f"Số dòng chuẩn bị lưu: {len(save_df):,}"
    )

    print(
        f"Số symbol: {save_df['symbol'].nunique()}"
    )

    # --------------------------------------------------------
    # 5. Lưu vào PostgreSQL
    # --------------------------------------------------------

    with engine.begin() as connection:

        print(
            "\nĐang xóa dữ liệu technical_indicators cũ..."
        )

        connection.execute(
            text(
                "TRUNCATE TABLE technical_indicators;"
            )
        )

        print(
            "Đang lưu dữ liệu mới..."
        )

        save_df.to_sql(
            "technical_indicators",
            con=connection,
            schema="public",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1000
        )

    print(
        "\nLưu technical indicators thành công!"
    )


# ============================================================
# Main
# ============================================================

def main():
    print("\nSAVE TECHNICAL INDICATORS")


    # --------------------------------------------------------
    # 1. Đọc stock_prices
    # --------------------------------------------------------

    print(
        "\n[1/4] Đọc dữ liệu stock_prices..."
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
        "\n[2/4] Tính technical indicators..."
    )

    result_df = (
        calculate_indicators_for_all_symbols(df)
    )

    print(
        "Đã tính xong indicators."
    )

    # --------------------------------------------------------
    # 3. Validate
    # --------------------------------------------------------

    print(
        "\n[3/4] Kiểm tra dữ liệu..."
    )

    validate_indicator_result(
        result_df
    )

    # --------------------------------------------------------
    # 4. Save
    # --------------------------------------------------------

    print(
        "\n[4/4] Lưu vào PostgreSQL..."
    )

    save_indicators(
        result_df
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
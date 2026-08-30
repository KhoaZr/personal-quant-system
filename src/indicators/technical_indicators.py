import numpy as np
import pandas as pd


# ============================================================
# SMA - Simple Moving Average
# ============================================================

def calculate_sma(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính Simple Moving Average.

    SMA20:
        Giá đóng cửa trung bình của 20 phiên gần nhất.

    SMA50:
        Giá đóng cửa trung bình của 50 phiên gần nhất.
    """

    df["sma20"] = (
        df["close"]
        .rolling(window=20, min_periods=20)
        .mean()
    )

    df["sma50"] = (
        df["close"]
        .rolling(window=50, min_periods=50)
        .mean()
    )

    return df


# ============================================================
# EMA - Exponential Moving Average
# ============================================================

def calculate_ema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính Exponential Moving Average.

    EMA đặt trọng số lớn hơn cho dữ liệu gần hiện tại.
    """

    df["ema20"] = (
        df["close"]
        .ewm(
            span=20,
            adjust=False,
            min_periods=20
        )
        .mean()
    )

    df["ema50"] = (
        df["close"]
        .ewm(
            span=50,
            adjust=False,
            min_periods=50
        )
        .mean()
    )

    return df


# ============================================================
# RSI - Relative Strength Index
# ============================================================

def calculate_rsi(
    df: pd.DataFrame,
    period: int = 14
) -> pd.DataFrame:
    """
    Tính Relative Strength Index (RSI).

    RSI đo động lượng tăng/giảm của giá.

    Giá trị thường nằm trong khoảng 0 - 100.

    Công thức:

        RS = Average Gain / Average Loss

        RSI = 100 - (100 / (1 + RS))

    Sử dụng Wilder's smoothing thông qua EMA:
        alpha = 1 / period
    """

    delta = df["close"].diff()

    # Chỉ lấy phần tăng
    gain = delta.clip(lower=0)

    # Chỉ lấy phần giảm
    loss = -delta.clip(upper=0)

    # Wilder's smoothing
    avg_gain = (
        gain
        .ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period
        )
        .mean()
    )

    avg_loss = (
        loss
        .ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period
        )
        .mean()
    )

    # Tránh chia cho 0
    rs = avg_gain.div(
        avg_loss.replace(0, np.nan)
    )

    df["rsi14"] = 100 - (
        100 / (1 + rs)
    )

    # Nếu average loss = 0 và average gain > 0
    # thì RSI = 100
    df.loc[
        (avg_loss == 0) & (avg_gain > 0),
        "rsi14"
    ] = 100.0

    return df


# ============================================================
# MACD
# ============================================================

def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính MACD.

    MACD = EMA12 - EMA26

    Signal = EMA9 của MACD

    Histogram = MACD - Signal
    """

    ema12 = (
        df["close"]
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        df["close"]
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    df["macd"] = ema12 - ema26

    df["macd_signal"] = (
        df["macd"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    df["macd_hist"] = (
        df["macd"]
        - df["macd_signal"]
    )

    return df


# ============================================================
# ATR - Average True Range
# ============================================================

def calculate_atr(
    df: pd.DataFrame,
    period: int = 14
) -> pd.DataFrame:
    """
    Tính Average True Range (ATR).

    ATR đo mức độ biến động của giá,
    không xác định hướng tăng hay giảm.

    True Range:

        TR = max(
            High - Low,
            abs(High - Previous Close),
            abs(Low - Previous Close)
        )

    ATR sử dụng Wilder's smoothing.
    """

    previous_close = df["close"].shift(1)

    high_low = (
        df["high"]
        - df["low"]
    )

    high_previous_close = (
        df["high"]
        - previous_close
    ).abs()

    low_previous_close = (
        df["low"]
        - previous_close
    ).abs()

    true_range = pd.concat(
        [
            high_low,
            high_previous_close,
            low_previous_close
        ],
        axis=1
    ).max(axis=1)

    df["atr14"] = (
        true_range
        .ewm(
            alpha=1 / period,
            adjust=False,
            min_periods=period
        )
        .mean()
    )

    return df


# ============================================================
# OBV - On-Balance Volume
# ============================================================

def calculate_obv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính On-Balance Volume (OBV).

    Nếu Close hôm nay > Close hôm qua:
        OBV += Volume

    Nếu Close hôm nay < Close hôm qua:
        OBV -= Volume

    Nếu Close hôm nay = Close hôm qua:
        OBV không thay đổi.
    """

    price_change = df["close"].diff()

    direction = np.sign(price_change)

    volume_change = (
        direction
        * df["volume"]
    )

    df["obv"] = (
        volume_change
        .fillna(0)
        .cumsum()
        .astype("int64")
    )

    return df


# ============================================================
# Bollinger Bands
# ============================================================

def calculate_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    num_std: int = 2
) -> pd.DataFrame:
    """
    Tính Bollinger Bands.

    Middle = SMA20

    Upper = Middle + 2 * Standard Deviation

    Lower = Middle - 2 * Standard Deviation
    """

    middle = (
        df["close"]
        .rolling(
            window=period,
            min_periods=period
        )
        .mean()
    )

    standard_deviation = (
        df["close"]
        .rolling(
            window=period,
            min_periods=period
        )
        .std()
    )

    df["bollinger_middle"] = middle

    df["bollinger_upper"] = (
        middle
        + num_std * standard_deviation
    )

    df["bollinger_lower"] = (
        middle
        - num_std * standard_deviation
    )

    return df


# ============================================================
# Calculate all technical indicators
# ============================================================

def calculate_all_indicators(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Tính toàn bộ technical indicators.

    Input:
        DataFrame chứa:
            symbol
            date
            open
            high
            low
            close
            volume

    Output:
        DataFrame chứa thêm:
            sma20
            sma50
            ema20
            ema50
            rsi14
            macd
            macd_signal
            macd_hist
            atr14
            obv
            bollinger_upper
            bollinger_middle
            bollinger_lower
    """

    required_columns = {
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume"
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Thiếu các cột bắt buộc: "
            f"{sorted(missing_columns)}"
        )

    # Không thay đổi DataFrame gốc
    df = df.copy()

    # Đảm bảo date là datetime
    df["date"] = pd.to_datetime(
        df["date"]
    )

    # Sắp xếp theo thời gian
    df = df.sort_values(
        "date"
    ).reset_index(drop=True)

    # Kiểm tra dữ liệu số
    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Tính từng nhóm indicator
    df = calculate_sma(df)

    df = calculate_ema(df)

    df = calculate_rsi(df)

    df = calculate_macd(df)

    df = calculate_atr(df)

    df = calculate_obv(df)

    df = calculate_bollinger_bands(df)

    return df
import numpy as np
import pandas as pd
# =====================================================================
# SMA - Simple Moving Average
# =====================================================================

def calculate_sma(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính Simple Moving Average.
    
    SMA20:
        Giá đóng cửa trung bình của 20 phiên gần nhất.
    
    SMA50:
        Giá đóng của trung bình của 50 phiên gần nhất.
    """
    df["sma20"] = (
        df["close"].rolling(window=20,min_periods=20).mean()
    )

    df["sma50"] = (
        df["close"].rolling(window=50,min_periods=50).mean()
    )

    return df

# ===================================================================
# EMA - Exponentail Moving Average
# ===================================================================

def caculate_ema(df: pd.DataFrame) -> pd.DataFrame:
   """
   Tính Exponential Moving Average
   EMA đặt trọng số lớn hơn cho dữ liệu gần hiện tại.
   """
   df["ema20"] = (
       df["close"].ewm(
           span=20,
           adjust=False,
           min_periods=20
       ).mean()
   )


   df["ema20"] = (
       df["close"].ewm(
           span=20,
           adjust=False,
           min_periods=20
       ).mean()
   )
   return df

# ==================================================================
# RSI - Relative Strength Index
# ==================================================================

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Tính Relative Strength Index (RSI).

    RSI đo động lượng tăng/giảm của giá.

    Giá trị thường nằm trong khoảng 0 - 100

    Công thức:

        RS = Average Gain / Average Loss

        RSI = 100 - (100 / (1 + RS))
    Sử dụng Wilder's smoothing thông qua EMA:
        alpha = 1 / period
    """

    delta = df["close"].diff()

    # chỉ lấy phần tăng
    gain = delta.clip(lower=0)

    # Chỉ lấy phần giảm
    loss = -delta.clip(upper=0)

    # Wilder's smoothing
    avg_gain = (
        gain.ewm(
            alpha= 1 / period,
            adjust= False,
            min_periods=period
        ).mean()
    )

    avg_loss = (
        gain.ewm(
            alpha= 1 / period,
            adjust=False,
            min_periods=period
        ).mean()
    )




from typing import Any

import numpy as np
import pandas as pd
import ta

from app.models.stock import StockPrice


class IndicatorService:
    @staticmethod
    def calculate_indicators(
        prices: list[StockPrice],
        symbol: str,
    ) -> list[dict[str, Any]]:
        """Tính toán chuỗi chỉ báo kỹ thuật từ danh sách giá OHLCV."""
        if len(prices) < 20:
            # Cần tối thiểu 20 phiên để tính toán chỉ báo cơ bản
            return []

        # 1. Chuyển đổi danh sách SQLAlchemy ORM sang Pandas DataFrame
        data = [
            {
                "date": price.date,
                "open": float(price.open),
                "high": float(price.high),
                "low": float(price.low),
                "close": float(price.close),
                "volume": float(price.volume),
            }
            for price in prices
        ]

        df = pd.DataFrame(data)

        # 2. Tính toán Moving Averages (SMA & EMA)
        df["sma20"] = ta.trend.sma_indicator(df["close"], window=20)
        df["sma50"] = ta.trend.sma_indicator(df["close"], window=50)
        df["ema20"] = ta.trend.ema_indicator(df["close"], window=20)
        df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)

        # 3. Tính toán Momentum (RSI)
        df["rsi14"] = ta.momentum.rsi(df["close"], window=14)

        # 4. Tính toán MACD
        macd_obj = ta.trend.MACD(df["close"])
        df["macd"] = macd_obj.macd()
        df["macd_signal"] = macd_obj.macd_signal()
        df["macd_hist"] = macd_obj.macd_diff()

        # 5. Tính toán Volatility (ATR & Bollinger Bands)
        df["atr14"] = ta.volatility.average_true_range(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=14,
        )

        bollinger = ta.volatility.BollingerBands(df["close"])
        df["bollinger_upper"] = bollinger.bollinger_hband()
        df["bollinger_middle"] = bollinger.bollinger_mavg()
        df["bollinger_lower"] = bollinger.bollinger_lband()

        # 6. Tính toán Volume Indicator (OBV)
        df["obv"] = ta.volume.on_balance_volume(
            df["close"],
            df["volume"],
        )

        # 7. Định dạng dữ liệu và xử lý giá trị NaN an toàn
        records: list[dict[str, Any]] = []

        def clean_num(val: Any) -> float | None:
            if pd.isna(val) or np.isnan(val):
                return None
            return round(float(val), 4)

        for _, row in df.iterrows():
            obv_val = row["obv"]
            obv_clean = (
                int(obv_val)
                if not pd.isna(obv_val) and not np.isnan(obv_val)
                else None
            )

            records.append(
                {
                    "symbol": symbol,
                    "date": row["date"],
                    "sma20": clean_num(row["sma20"]),
                    "sma50": clean_num(row["sma50"]),
                    "ema20": clean_num(row["ema20"]),
                    "ema50": clean_num(row["ema50"]),
                    "rsi14": clean_num(row["rsi14"]),
                    "macd": clean_num(row["macd"]),
                    "macd_signal": clean_num(row["macd_signal"]),
                    "macd_hist": clean_num(row["macd_hist"]),
                    "atr14": clean_num(row["atr14"]),
                    "obv": obv_clean,
                    "bollinger_upper": clean_num(row["bollinger_upper"]),
                    "bollinger_middle": clean_num(row["bollinger_middle"]),
                    "bollinger_lower": clean_num(row["bollinger_lower"]),
                }
            )

        return records

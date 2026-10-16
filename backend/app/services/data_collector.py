import logging
from datetime import date, datetime
from typing import Any, cast

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class DataCollectorService:
    @staticmethod
    def fetch_stock_prices(
        symbol: str,
        period: str = "2y",
    ) -> pd.DataFrame:
        """Thu thập dữ liệu lịch sử giá từ Yahoo Finance."""
        logger.info(f"Fetching data for symbol: {symbol} with period: {period}")

        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        if df.empty:
            logger.warning(f"No data returned for symbol: {symbol}")
            return pd.DataFrame()

        df.reset_index(inplace=True)

        return cast(pd.DataFrame, df)

    @staticmethod
    def validate_and_clean_prices(
        df: pd.DataFrame,
        symbol: str,
    ) -> list[dict[str, Any]]:
        """Làm sạch và kiểm định tính hợp lệ của dữ liệu OHLCV."""

        if df.empty:
            return []

        cleaned_records: list[dict[str, Any]] = []

        for _, row in df.iterrows():
            raw_date = row.get("Date")

            if pd.isna(raw_date):
                continue

            price_date: date = (
                raw_date.date() if isinstance(raw_date, (datetime, pd.Timestamp)) else raw_date
            )

            open_p = float(row.get("Open", 0))
            high_p = float(row.get("High", 0))
            low_p = float(row.get("Low", 0))
            close_p = float(row.get("Close", 0))
            adj_close_p = float(row.get("Adj Close", close_p))
            volume_val = int(row.get("Volume", 0))

            # Rule 1: Kiểm tra giá phải lớn hơn 0.
            if open_p <= 0 or high_p <= 0 or low_p <= 0 or close_p <= 0:
                logger.warning(f"Invalid price <= 0 for {symbol} on {price_date}")
                continue

            # Rule 2: Kiểm tra tính nhất quán OHLC.
            # High >= Open/Close và Low <= Open/Close.
            if high_p < max(open_p, close_p) or low_p > min(open_p, close_p):
                logger.warning(f"OHLC inconsistency for {symbol} on {price_date}")
                continue

            cleaned_records.append(
                {
                    "symbol": symbol,
                    "date": price_date,
                    "open": round(open_p, 2),
                    "high": round(high_p, 2),
                    "low": round(low_p, 2),
                    "close": round(close_p, 2),
                    "adj_close": round(adj_close_p, 2),
                    "volume": volume_val,
                }
            )

        return cleaned_records

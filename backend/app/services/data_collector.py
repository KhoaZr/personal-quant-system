from datetime import UTC, datetime

import pandas as pd
import yfinance as yf


def get_data_today(symbol: str) -> pd.DataFrame:
    df = yf.download(
        tickers=symbol,
        period="1d",
        interval="1d",
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df


def get_data(symbol: str) -> pd.DataFrame:
    df = yf.download(
        tickers=symbol,
        start="2010-01-01",
        end=datetime.now(UTC).strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    return df
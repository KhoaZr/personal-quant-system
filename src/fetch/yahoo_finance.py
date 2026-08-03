import yfinance as yf
from datetime import datetime
import pandas as pd
def get_data_today(symbol):
    df = yf.download(
        tickers=symbol,
        period="1d",
        interval="1d"
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def get_data(symbol):
    df = yf.download(
        tickers=symbol,
        start="2010-01-01",
        end=datetime.today().strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        progress=False
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df
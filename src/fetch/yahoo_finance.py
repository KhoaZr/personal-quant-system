import yfinance as yf
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


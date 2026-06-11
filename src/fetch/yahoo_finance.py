import yfinance as yf
def get_data_today(symbol):
    df = yf.download(
        tickers=symbol,
        period="1d",
        interval="1d"
    )
    return df


import pandas as pd
from sqlalchemy import text

from sqlalchemy import select

from sqlalchemy.orm import Session


from src.database.db import engine


from src.database.models import Stock, StockPrice

# ==============================
# 1. Cấu hình
# ==============================

INPUT_FILE = "data/clean/FPT.VN.cleaned.csv"


# ==============================
# 2. Đọc dữ liệu.
# ==============================

df = pd.read_csv(INPUT_FILE)

print(f"Đã đọc {len(df)} dòng từ {INPUT_FILE}");


df["date"] = pd.to_datetime(df["date"]).dt.date

with Session(engine) as session:
    for _, row in df.iterrows():

        symbol = row["symbol"]

        # Kiểm tra stock tồn tại:

        stock = session.scalar(
            select(Stock).where(
                Stock.symbol == symbol
            )
        )
        if stock is None:
            raise ValueError(
                f"Stock {symbol} chưa tồn tại trong bảng stocks"
            )

        existing_price = session.scalar(
            select(StockPrice).where(
                StockPrice.symbol == symbol,
                StockPrice.date == row["date"]
            )
        )

        if existing_price is not None:
            continue

        stock_price = StockPrice(
            symbol = symbol,
            date = row["date"],
            open = row["open"],
            high = row["high"],
            low = row["low"],
            close = row["close"], 
            adj_close = row["adj_close"],
            volume = row["volume"],
        )

        session.add(stock_price)

    session.commit()
print("Lưu dữ liệu vào postgres thành công!")
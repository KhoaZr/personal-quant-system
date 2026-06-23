import pandas as pd
from src.database.db import engine
df = pd.read_csv("data/raw/data_a_day.csv")

df.to_sql(
    name="stock_prices",
    con=engine,
    if_exists="append",
    index=False
    )
print("Lưu dữ liệu thành công!")
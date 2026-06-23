from src.fetch.yahoo_finance import(
    get_data_today
)

from src.process.stock_processor import(
    process_stock_data
)
import pandas as pd
def main():
    all_data = []
    symbols = ["TCB.VN","FPT.VN"]
    for symbol in symbols:
        df = get_data_today(symbol)
        df_process = process_stock_data(df.copy(),symbol)
        path_df_process = f"data/raw/data_a_day.csv"
        all_data.append(df_process)
    final_data = pd.concat(all_data, ignore_index=True)
    final_data.to_csv(path_df_process,index = False)
if __name__ == "__main__":
    main()
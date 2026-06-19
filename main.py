from src.fetch.yahoo_finance import(
    get_data_today
)

from src.process.stock_processor import(
    process_stock_data
)
import pandas as pd
def main():
    symbol = "TCB.VN"
    df = get_data_today(symbol)
    data_file_path = f"data/raw/{symbol}.csv"
    df.to_csv(
        data_file_path
    )
    df_process = pd.read_csv(data_file_path)
    df_process = process_stock_data(df_process,symbol)
    data_processed_file_path = f"data/raw/{symbol}_processed.csv"
    df_process.to_csv(data_processed_file_path, index=False)
    print(df_process.head())
if __name__ == "__main__":
    main()
from src.fetch.yahoo_finance import(
    get_data_today
)
def main():
    symbol = "TCB.VN"
    df = get_data_today(symbol)
    data_file_path = f"data/raw/{symbol}.csv"
    df.to_csv(
        data_file_path
    )
if __name__ == "__main__":
    main()
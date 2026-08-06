from src.fetch.yahoo_finance import(
    get_data_today,
    get_data
)

from src.process.stock_processor import(
    process_stock_data
)
import pandas as pd
def main():
    all_data = []
    # symbols = ["TCB.VN","FPT.VN","BVH.VN","BVH.VN","GAS.VN","HPG.VN","MSN.VN","PLX.VN","POW.VN","SAB.VN","VCB.VN","VIC.VN"]
    # for symbol in symbols:
    #     df = get_data_today(symbol)
    #     df_process = process_stock_data(df.copy(),symbol)
    #     path_df_process = f"data/raw/data_a_day.csv"
    #     all_data.append(df_process)
    # final_data = pd.concat(all_data, ignore_index=True)
    # final_data.to_csv(path_df_process,index = False)
    symbol = "FPT.VN"
    df = get_data(symbol)
    # df.to_csv(f"data/raw/{symbol}.csv")

    import seaborn as sns
    import matplotlib.pyplot as plt

    khoa = pd.read_csv("./data/raw/FPT.VN.csv")

    # Chuyển Date sang datetime
    khoa["Date"] = pd.to_datetime(khoa["Date"])

    # Chuyển Date thành số
    khoa["date_num"] = khoa["Date"].map(pd.Timestamp.toordinal)

    # Ma trận tương quan
    corr = khoa[
        ["date_num", "Open", "High", "Low", "Close", "Volume"]
    ].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)

    plt.title("Correlation Matrix - FPT.VN")
    plt.show()

if __name__ == "__main__":
    main()
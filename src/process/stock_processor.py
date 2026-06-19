import pandas as pd
def process_stock_data(df,symbol):
    """Chuẩn hóa dữ liệu cổ phiếu"""
    # Chuyển dữ liệu thành cột
    df = df.reset_index()
    
    # Chuẩn hóa tên cột
    df.columns = [
        col.lower()
        for col in df.columns
    ]

    # Thêm cột mã cổ phiếu

    df["symbol"] = symbol
    return df

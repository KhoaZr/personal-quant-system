from src.process.stock_processor import process_csv_file
import os

if __name__ == '__main__':
    os.makedirs('data/clean', exist_ok=True)
    cleaned = process_csv_file('data/raw/FPT.VN.csv', 'data/clean/FPT.VN.cleaned.csv', 'FPT.VN')
    print(f"Cleaned rows: {len(cleaned)}")

import pandas as pd
from sqlalchemy import text

from src.database.db import engine


# ==============================
# 1. Cấu hình
# ==============================

INPUT_FILE = "data/clean/FPT.VN.cleaned.csv"


# ==============================
# 2. Đọc dữ liệu.
# ==============================

df = pd.read_csv(INPUT_FILE)

print(f"Đã đọc {len(df)} dòng từ {INPUT_FILE}");
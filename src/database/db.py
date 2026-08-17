import os

from dotenv import load_dotenv

from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL chưa có trong file env"
    )

engine = create_engine(
    DATABASE_URL,
    echo=False
    )
print("Lưu dữ liệu thành công!")
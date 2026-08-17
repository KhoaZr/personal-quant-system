from src.database.db import engine
from src.database.models import Base


def create_tables():
    print("Đang tạo tables...")

    Base.metadata.create_all(engine)

    print("Tạo tables thành công!")


if __name__ == "__main__":
    create_tables()
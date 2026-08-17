from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Boolean,
    Numeric
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
# ==================================
# Base
# ==================================

class Base(DeclarativeBase):
    pass



# ==================================
# Stock
# ==================================

class Stock(Base):
    __tablename__ = "stocks"

    symbol: Mapped[String] = mapped_column(
        String(20),
        primary_key=True
    )

    # Tên công ty
    company_name: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )

    # Sàn giao dịch
    exchange_id: Mapped[int] =  mapped_column(
        Integer,
        nullable=False
    )

    # Ngành
    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    # Chi tiết ngành
    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    # Ngày niêm yết
    listing_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True
    )
    # Tiền tệ
    currency: Mapped[str |None] = mapped_column(
        String(10),
        nullable=True
    )
    # Trạng thái hoạt động
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    create_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

# ================================================
# stock_price
# ================================================

class StockPrice(Base):
    __tablename__ = "stock_prices"

    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol"),
        primary_key=True
    )

    date: Mapped[Date] = mapped_column(
        Date,
        primary_key=True
    )

    open: Mapped[float] = mapped_column(
        Numeric(12,2),
        nullable=True
    )
    high: Mapped[float] = mapped_column(
        Numeric(12,2),
        nullable=True
    )
    low: Mapped[float] = mapped_column(
        Numeric(12,2),
        nullable=True
    )
    close: Mapped[float] = mapped_column(
        Numeric(12,2),
        nullable=True
    )
    adj_close: Mapped[float] = mapped_column(
        Numeric(12,2),
        nullable=True
    )
    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )  
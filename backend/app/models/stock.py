from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ==========================================
# 1. CORE MARKET DATA
#    (Từ ERD database_Stock.png)

# ==========================================


class Exchange(Base):
    __tablename__ = "exchanges"
    exchange_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    country: Mapped[str | None] = mapped_column(String(50))
    timezone: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    stocks: Mapped[list["Stock"]] = relationship(
        "Stock",
        back_populates="exchange_rel",
    )


class Stock(Base):
    __tablename__ = "stocks"
    symbol: Mapped[str] = mapped_column(
        String(20),
        primary_key=True,
        index=True,
    )
    company_name: Mapped[str | None] = mapped_column(
        String(255),
    )
    exchange_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("exchanges.exchange_id"),
    )
    sector: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(100))
    listing_date: Mapped[date | None] = mapped_column(Date)
    currency: Mapped[str | None] = mapped_column(
        String(10),
        default="VND",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    exchange_rel: Mapped["Exchange | None"] = relationship(
        "Exchange",
        back_populates="stocks",
    )
    prices: Mapped[list["StockPrice"]] = relationship(
        "StockPrice",
        back_populates="stock",
        cascade="all, delete-orphan",
    )
    indicators: Mapped[list["TechnicalIndicator"]] = relationship(
        "TechnicalIndicator",
        back_populates="stock",
        cascade="all, delete-orphan",
    )


class StockPrice(Base):
    __tablename__ = "stock_prices"
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
        primary_key=True,
    )
    date: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
    )
    open: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    high: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    low: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    close: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    adj_close: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
    )
    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    stock: Mapped["Stock"] = relationship(
        "Stock",
        back_populates="prices",
    )


class TechnicalIndicator(Base):
    __tablename__ = "technical_indicators"
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
        primary_key=True,
    )
    date: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
    )
    sma20: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    sma50: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    ema20: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    ema50: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    rsi14: Mapped[float | None] = mapped_column(
        Numeric(8, 4),
    )
    macd: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    macd_signal: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    macd_hist: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    atr14: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    obv: Mapped[int | None] = mapped_column(BigInteger)
    bollinger_upper: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    bollinger_middle: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    bollinger_lower: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    stock: Mapped["Stock"] = relationship(
        "Stock",
        back_populates="indicators",
    )


# ==========================================
# 2. FUNDAMENTAL, NEWS & MACRO
#    (Từ ERD database_Stock.png)

# ==========================================


class CompanyFinancial(Base):
    __tablename__ = "company_financials"
    financial_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
    )
    report_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    fiscal_year: Mapped[int | None] = mapped_column(Integer)
    fiscal_quarter: Mapped[int | None] = mapped_column(Integer)
    eps: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    pe: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    pb: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    roe: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    roa: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    debt_to_equity: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    revenue: Mapped[float | None] = mapped_column(
        Numeric(18, 2),
    )
    net_income: Mapped[float | None] = mapped_column(
        Numeric(18, 2),
    )
    gross_margin: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    operating_margin: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class News(Base):
    __tablename__ = "news"
    news_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(
        String(100),
    )
    author: Mapped[str | None] = mapped_column(
        String(100),
    )
    url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class NewsSentiment(Base):
    __tablename__ = "news_sentiments"
    sentiment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.news_id", ondelete="CASCADE"),
    )
    model_name: Mapped[str | None] = mapped_column(
        String(100),
    )
    sentiment: Mapped[str | None] = mapped_column(
        String(20),
    )  # POSITIVE, NEGATIVE, NEUTRAL
    score: Mapped[float | None] = mapped_column(
        Numeric(6, 4),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"
    macro_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    indicator_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    country: Mapped[str | None] = mapped_column(
        String(50),
    )
    indicator_name: Mapped[str | None] = mapped_column(
        String(100),
    )
    value: Mapped[float | None] = mapped_column(
        Numeric(18, 4),
    )
    unit: Mapped[str | None] = mapped_column(
        String(30),
    )
    source: Mapped[str | None] = mapped_column(
        String(100),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    prediction_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
    )
    model_name: Mapped[str | None] = mapped_column(
        String(100),
    )
    predict_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    target_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    predicted_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
    )
    actual_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
    )
    mae: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    rmse: Mapped[float | None] = mapped_column(
        Numeric(12, 4),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


# ==========================================
# 3. PRODUCTION QUANT & FEEDBACK EXTENSIONS
#    (Master Plan v2)

# ==========================================


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )
    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    parameters: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    action: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )  # BUY, SELL, HOLD
    confidence: Mapped[float] = mapped_column(
        Numeric(6, 4),
        nullable=False,
    )
    reasoning: Mapped[str | None] = mapped_column(Text)


class TradePlan(Base):
    __tablename__ = "trade_plans"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("stocks.symbol", ondelete="CASCADE"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    entry_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    stop_loss: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    take_profit: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    position_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    risk_reward_ratio: Mapped[float] = mapped_column(
        Numeric(6, 2),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
    )


class PaperTrade(Base):
    __tablename__ = "paper_trades"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    trade_plan_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("trade_plans.id"),
    )
    symbol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    entry_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    exit_time: Mapped[datetime | None] = mapped_column(
        DateTime,
    )
    actual_entry_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    actual_exit_price: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    pnl: Mapped[float | None] = mapped_column(
        Numeric(14, 2),
    )
    pnl_percentage: Mapped[float | None] = mapped_column(
        Numeric(8, 4),
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="OPEN",
    )


class FeedbackDataset(Base):
    __tablename__ = "feedback_dataset"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    paper_trade_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("paper_trades.id"),
    )
    feature_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
    )
    predicted_action: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    actual_outcome: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

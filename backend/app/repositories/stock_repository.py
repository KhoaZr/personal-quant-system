from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.stock import Stock, StockPrice


class StockRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_stocks(self) -> list[Stock]:
        """Lấy danh sách tất cả cổ phiếu đang hoạt động."""
        stmt = select(Stock).where(Stock.is_active.is_(True))
        return list(self.db.scalars(stmt).all())

    def get_stock_by_symbol(self, symbol: str) -> Stock | None:
        """Tìm cổ phiếu theo mã symbol."""
        stmt = select(Stock).where(Stock.symbol == symbol)
        return self.db.scalars(stmt).first()

    def upsert_stock(
        self,
        symbol: str,
        company_name: str | None = None,
        sector: str | None = None,
    ) -> Stock:
        """Thêm mới hoặc cập nhật thông tin cổ phiếu."""
        stock = self.get_stock_by_symbol(symbol)

        if not stock:
            stock = Stock(
                symbol=symbol,
                company_name=company_name,
                sector=sector,
                is_active=True,
            )
            self.db.add(stock)
        else:
            if company_name:
                stock.company_name = company_name

            if sector:
                stock.sector = sector

        self.db.commit()
        self.db.refresh(stock)

        return stock

    def bulk_upsert_stock_prices(
        self,
        price_records: list[dict[str, Any]],
    ) -> int:
        """Upsert (thêm/cập nhật) danh sách giá OHLCV vào Supabase."""
        if not price_records:
            return 0

        stmt = insert(StockPrice).values(price_records)

        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol", "date"],
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "adj_close": stmt.excluded.adj_close,
                "volume": stmt.excluded.volume,
            },
        )

        self.db.execute(stmt)
        self.db.commit()

        return len(price_records)

    def get_latest_price_date(self, symbol: str) -> date | None:
        """Lấy ngày có dữ liệu giá mới nhất của một mã cổ phiếu."""
        stmt = (
            select(StockPrice.date)
            .where(StockPrice.symbol == symbol)
            .order_by(StockPrice.date.desc())
            .limit(1)
        )

        return self.db.scalars(stmt).first()

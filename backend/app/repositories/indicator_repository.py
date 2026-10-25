from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.stock import StockPrice, TechnicalIndicator


class IndicatorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_prices_by_symbol(self, symbol: str) -> list[StockPrice]:
        """Lấy danh sách giá lịch sử của một mã cổ phiếu được sắp xếp theo thời gian tăng dần."""
        stmt = select(StockPrice).where(StockPrice.symbol == symbol).order_by(StockPrice.date.asc())

        return list(self.db.scalars(stmt).all())

    def bulk_upsert_indicators(self, records: list[dict[str, Any]]) -> int:
        """Thêm mới hoặc cập nhật danh sách chỉ báo kỹ thuật vào Supabase."""
        if not records:
            return 0

        stmt = insert(TechnicalIndicator).values(records)

        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol", "date"],
            set_={
                "sma20": stmt.excluded.sma20,
                "sma50": stmt.excluded.sma50,
                "ema20": stmt.excluded.ema20,
                "ema50": stmt.excluded.ema50,
                "rsi14": stmt.excluded.rsi14,
                "macd": stmt.excluded.macd,
                "macd_signal": stmt.excluded.macd_signal,
                "macd_hist": stmt.excluded.macd_hist,
                "atr14": stmt.excluded.atr14,
                "obv": stmt.excluded.obv,
                "bollinger_upper": stmt.excluded.bollinger_upper,
                "bollinger_middle": stmt.excluded.bollinger_middle,
                "bollinger_lower": stmt.excluded.bollinger_lower,
            },
        )

        self.db.execute(stmt)
        self.db.commit()

        return len(records)


from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import PaperTrade


class PaperTradeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_paper_trade(
        self,
        trade_data: dict[str, Any],
    ) -> PaperTrade:
        """Tạo lệnh Paper Trade mới ở trạng thái OPEN."""
        trade = PaperTrade(**trade_data)

        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)

        return trade

    def get_open_trades(
        self,
        symbol: str | None = None,
    ) -> list[PaperTrade]:
        """Lấy danh sách các lệnh đang mở."""
        stmt = select(PaperTrade).where(
            PaperTrade.status == "OPEN",
        )

        if symbol:
            stmt = stmt.where(
                PaperTrade.symbol == symbol,
            )

        return list(self.db.scalars(stmt).all())

    def get_trade_by_id(
        self,
        trade_id: int,
    ) -> PaperTrade | None:
        """Tìm lệnh Paper Trade theo ID."""
        stmt = select(PaperTrade).where(
            PaperTrade.id == trade_id,
        )

        return self.db.scalars(stmt).first()

    def close_paper_trade(
        self,
        trade_id: int,
        actual_exit: float,
        exit_time: datetime,
        fees: float = 0.0,
    ) -> PaperTrade | None:
        """Đóng lệnh mô phỏng và tính PnL, tỷ suất lợi nhuận."""
        trade = self.get_trade_by_id(trade_id)

        if trade is None or trade.status != "OPEN":
            return None

        entry_price = float(trade.actual_entry_price)
        exit_price = actual_exit
        quantity = int(trade.quantity)

        if entry_price <= 0:
            raise ValueError(
                "Giá vào lệnh phải lớn hơn 0.",
            )

        # Tính lợi nhuận sau phí.
        gross_pnl = (
            exit_price - entry_price
        ) * quantity
        net_pnl = gross_pnl - fees

        # Tỷ suất lợi nhuận ròng trên vốn vào lệnh.
        return_pct = (
            net_pnl / (entry_price * quantity)
        ) * 100

        trade.actual_exit_price = exit_price
        trade.exit_time = exit_time
        trade.pnl = round(net_pnl, 2)
        trade.pnl_percentage = round(return_pct, 4)
        trade.status = "CLOSED"

        try:
            self.db.commit()
            self.db.refresh(trade)
        except Exception:
            self.db.rollback()
            raise

        return trade

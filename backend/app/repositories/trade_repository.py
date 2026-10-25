from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import Signal, TradePlan


class TradeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_signal(self, signal_data: dict[str, Any]) -> Signal:
        """Lưu tín hiệu giao dịch mới vào CSDL Supabase."""
        signal = Signal(**signal_data)

        self.db.add(signal)
        self.db.commit()
        self.db.refresh(signal)

        return signal

    def save_trade_plan(self, plan_data: dict[str, Any]) -> TradePlan:
        """Lưu kế hoạch giao dịch chi tiết vào CSDL Supabase."""
        plan = TradePlan(**plan_data)

        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        return plan

    def get_latest_signals(self, symbol: str) -> list[Signal]:
        """Lấy danh sách tín hiệu giao dịch mới nhất của cổ phiếu."""
        stmt = (
            select(Signal)
            .where(Signal.symbol == symbol)
            .order_by(Signal.timestamp.desc())
            .limit(10)
        )

        return list(self.db.scalars(stmt).all())

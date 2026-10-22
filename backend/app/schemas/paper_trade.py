
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OpenPaperTradeRequest(BaseModel):
    symbol: str
    trade_plan_id: int | None = None
    actual_entry: float
    quantity: int
    entry_time: datetime | None = None


class ClosePaperTradeRequest(BaseModel):
    trade_id: int
    actual_exit: float
    exit_time: datetime | None = None
    fees: float = 0.0


class PaperTradeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trade_id: int = Field(validation_alias="id")
    symbol: str
    status: str

    actual_entry: float = Field(
        validation_alias="actual_entry_price",
    )
    actual_exit: float | None = Field(
        default=None,
        validation_alias="actual_exit_price",
    )

    quantity: int
    pnl: float | None = None
    return_pct: float | None = Field(
        default=None,
        validation_alias="pnl_percentage",
    )

    entry_time: datetime
    exit_time: datetime | None = None

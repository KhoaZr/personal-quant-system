from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockBase(BaseModel):
    symbol: str
    company_name: str | None = None
    sector: str | None = None
    is_active: bool = True


class StockCreate(StockBase):
    pass


class StockResponse(StockBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CollectDataRequest(BaseModel):
    symbols: list[str]
    period: str = "2y"


class CollectDataResponse(BaseModel):
    status: str
    processed_symbols: list[str]
    total_records_inserted: int

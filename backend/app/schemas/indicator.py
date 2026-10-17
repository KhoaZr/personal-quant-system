
from pydantic import BaseModel


class CalculateIndicatorRequest(BaseModel):
    symbols: list[str]


class CalculateIndicatorResponse(BaseModel):
    status: str
    processed_symbols: list[str]
    total_records_inserted: int

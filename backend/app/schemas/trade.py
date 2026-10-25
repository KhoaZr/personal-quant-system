from typing import Any

from pydantic import BaseModel


class GenerateSignalRequest(BaseModel):
    symbols: list[str]
    account_risk_limit: float = 500.0


class SignalItem(BaseModel):
    symbol: str
    action: str
    confidence: float
    reasoning: str | None = None
    trade_plan: dict[str, Any] | None = None


class GenerateSignalResponse(BaseModel):
    status: str
    signals: list[SignalItem]

from datetime import date

from pydantic import BaseModel


class PredictRequest(BaseModel):
    symbols: list[str]


class PredictionItem(BaseModel):
    symbol: str
    date: date
    probability_up: float
    predicted_signal: int
    confidence_score: float


class PredictResponse(BaseModel):
    status: str
    model_version: str
    predictions: list[PredictionItem]

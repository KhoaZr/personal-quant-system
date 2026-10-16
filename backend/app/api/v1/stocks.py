from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.stock_repository import StockRepository
from app.schemas.stock import (
    CollectDataRequest,
    CollectDataResponse,
    StockCreate,
    StockResponse,
)
from app.services.data_collector import DataCollectorService

router = APIRouter(prefix="/stocks", tags=["Stocks"])

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[StockResponse])
def list_stocks(
    db: DbSession,
) -> list[StockResponse]:
    """Lấy danh sách cổ phiếu trong hệ thống."""
    repo = StockRepository(db)
    stocks = repo.get_active_stocks()

    return [StockResponse.model_validate(s) for s in stocks]


@router.post(
    "/",
    response_model=StockResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_stock(
    stock_in: StockCreate,
    db: DbSession,
) -> StockResponse:
    """Thêm mã cổ phiếu mới vào danh sách."""
    repo = StockRepository(db)

    stock = repo.upsert_stock(
        symbol=stock_in.symbol.upper(),
        company_name=stock_in.company_name,
        sector=stock_in.sector,
    )

    return StockResponse.model_validate(stock)


@router.post(
    "/collect",
    response_model=CollectDataResponse,
)
def collect_stock_data(
    payload: CollectDataRequest,
    db: DbSession,
) -> CollectDataResponse:
    """Thu thập dữ liệu giá OHLCV và lưu tự động vào Supabase."""
    repo = StockRepository(db)

    total_inserted = 0
    successful_symbols: list[str] = []

    for sym in payload.symbols:
        symbol_upper = sym.upper()

        repo.upsert_stock(symbol=symbol_upper)

        df_raw = DataCollectorService.fetch_stock_prices(
            symbol_upper,
            period=payload.period,
        )

        cleaned_records = DataCollectorService.validate_and_clean_prices(
            df_raw,
            symbol_upper,
        )

        if cleaned_records:
            inserted = repo.bulk_upsert_stock_prices(cleaned_records)

            total_inserted += inserted
            successful_symbols.append(symbol_upper)

    return CollectDataResponse(
        status="success",
        processed_symbols=successful_symbols,
        total_records_inserted=total_inserted,
    )

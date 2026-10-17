
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.indicator_repository import IndicatorRepository
from app.schemas.indicator import (
    CalculateIndicatorRequest,
    CalculateIndicatorResponse,
)
from app.services.indicator_service import IndicatorService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/indicators",
    tags=["Technical Indicators"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/calculate",
    response_model=CalculateIndicatorResponse,
)
def calculate_indicators(
    payload: CalculateIndicatorRequest,
    db: DbSession,
) -> CalculateIndicatorResponse:
    """Tính toán và tự động lưu các chỉ báo kỹ thuật cho danh sách cổ phiếu."""
    repo = IndicatorRepository(db)
    total_inserted = 0
    successful_symbols: list[str] = []

    for sym in payload.symbols:
        symbol_upper = sym.upper()

        try:
            prices = repo.get_prices_by_symbol(symbol_upper)

            if not prices:
                logger.warning("No price records found for %s", symbol_upper)
                continue

            indicator_records = IndicatorService.calculate_indicators(
                prices,
                symbol_upper,
            )

            if indicator_records:
                inserted = repo.bulk_upsert_indicators(indicator_records)
                total_inserted += inserted
                successful_symbols.append(symbol_upper)

        except Exception as e:
            db.rollback()

            logger.exception(
                "Error calculating indicators for %s",
                symbol_upper,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi tính chỉ báo cho {symbol_upper}: {e}",
            ) from e

    return CalculateIndicatorResponse(
        status="success",
        processed_symbols=successful_symbols,
        total_records_inserted=total_inserted,
    )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.backtest import BacktestRequest, BacktestResponse
from app.services.backtest_service import BacktestService

router = APIRouter(
    prefix="/backtest",
    tags=["Backtesting Engine"],
)


@router.post("/run", response_model=BacktestResponse)
def run_strategy_backtest(
    payload: BacktestRequest,
    db: Session = Depends(get_db),  # noqa: B008
) -> BacktestResponse:
    """
    Thực thi kiểm thử chiến lược định lượng trên dữ liệu lịch sử.
    """
    try:
        return BacktestService.run_backtest(
            db=db,
            request=payload,
        )

    except ValueError as val_err:
        raise HTTPException(
            status_code=400,
            detail=str(val_err),
        ) from val_err

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi thực thi backtest: {err!s}",
        ) from err

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.paper_trade_repository import PaperTradeRepository
from app.schemas.paper_trade import (
    ClosePaperTradeRequest,
    OpenPaperTradeRequest,
    PaperTradeResponse,
)
from app.services.feedback_service import FeedbackService

router = APIRouter(
    prefix="/paper-trades",
    tags=["Paper Trading & Feedback"],
)


@router.post(
    "/open",
    response_model=PaperTradeResponse,
    status_code=status.HTTP_201_CREATED,
)
def open_paper_trade(
    payload: OpenPaperTradeRequest,
    db: Session = Depends(get_db), # noqa: B008
) -> PaperTradeResponse:
    """Khởi tạo lệnh giao dịch mô phỏng ở trạng thái OPEN."""
    repo = PaperTradeRepository(db)

    trade_data = {
        "symbol": payload.symbol.upper(),
        "trade_plan_id": payload.trade_plan_id,
        "actual_entry_price": payload.actual_entry,
        "quantity": payload.quantity,
        "entry_time": payload.entry_time or datetime.now(UTC),
        "status": "OPEN",
    }

    trade = repo.create_paper_trade(trade_data)

    return PaperTradeResponse.model_validate(trade)


@router.post(
    "/close",
    response_model=PaperTradeResponse,
)
def close_paper_trade(
    payload: ClosePaperTradeRequest,
    db: Session = Depends(get_db), # noqa: B008
) -> PaperTradeResponse:
    """Đóng lệnh mô phỏng và tạo Feedback Dataset."""
    repo = PaperTradeRepository(db)

    exit_time = payload.exit_time or datetime.now(UTC)

    trade = repo.close_paper_trade(
        trade_id=payload.trade_id,
        actual_exit=payload.actual_exit,
        exit_time=exit_time,
        fees=payload.fees,
    )

    if trade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Không tìm thấy lệnh OPEN với "
                f"trade_id = {payload.trade_id}"
            ),
        )

    FeedbackService.record_feedback_from_trade(db, trade)

    return PaperTradeResponse.model_validate(trade)


@router.get(
    "/open-trades",
    response_model=list[PaperTradeResponse],
)
def list_open_trades(
    db: Session = Depends(get_db), # noqa: B008
) -> list[PaperTradeResponse]:
    """Lấy danh sách các lệnh giao dịch mô phỏng đang mở."""
    repo = PaperTradeRepository(db)
    trades = repo.get_open_trades()

    return [
        PaperTradeResponse.model_validate(trade)
        for trade in trades
    ]

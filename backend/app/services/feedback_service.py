import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import (
    FeedbackDataset,
    PaperTrade,
    StockPrice,
    TechnicalIndicator,
)

logger = logging.getLogger(__name__)


class FeedbackService:
    """Xử lý dữ liệu phản hồi từ các giao dịch Paper Trading."""

    @staticmethod
    def record_feedback_from_trade(
        db: Session,
        paper_trade: PaperTrade,
    ) -> FeedbackDataset | None:
        """Tạo feedback từ giao dịch mô phỏng đã đóng.

        actual_outcome:
            1: Giao dịch có lãi.
            0: Giao dịch lỗ hoặc hòa vốn.
        """

        # Chỉ ghi nhận giao dịch đã đóng.
        if paper_trade.status != "CLOSED":
            logger.warning(
                "Trade %s is not CLOSED; feedback skipped.",
                paper_trade.id,
            )
            return None

        # Chưa có PnL thì chưa thể xác định kết quả.
        if paper_trade.pnl is None:
            logger.warning(
                "Trade %s has no PnL; feedback skipped.",
                paper_trade.id,
            )
            return None

        # Tránh tạo nhiều feedback cho cùng một giao dịch.
        existing_feedback = db.scalar(
            select(FeedbackDataset).where(FeedbackDataset.paper_trade_id == paper_trade.id)
        )

        if existing_feedback is not None:
            logger.info(
                "Feedback already exists for trade_id=%s.",
                paper_trade.id,
            )
            return existing_feedback

        symbol = paper_trade.symbol

        try:
            # Lấy chỉ báo kỹ thuật mới nhất.
            latest_indicator = db.scalars(
                select(TechnicalIndicator)
                .where(TechnicalIndicator.symbol == symbol)
                .order_by(TechnicalIndicator.date.desc())
                .limit(1)
            ).first()

            # Lấy giá cổ phiếu mới nhất.
            latest_price = db.scalars(
                select(StockPrice)
                .where(StockPrice.symbol == symbol)
                .order_by(StockPrice.date.desc())
                .limit(1)
            ).first()

            # Tạo snapshot đặc trưng.
            features_snapshot: dict[str, Any] = {
                "close": (
                    float(latest_price.close)
                    if latest_price is not None and latest_price.close is not None
                    else 0.0
                ),
                "rsi14": (
                    float(latest_indicator.rsi14)
                    if latest_indicator is not None and latest_indicator.rsi14 is not None
                    else 0.0
                ),
                "macd": (
                    float(latest_indicator.macd)
                    if latest_indicator is not None and latest_indicator.macd is not None
                    else 0.0
                ),
                "sma20": (
                    float(latest_indicator.sma20)
                    if latest_indicator is not None and latest_indicator.sma20 is not None
                    else 0.0
                ),
                "atr14": (
                    float(latest_indicator.atr14)
                    if latest_indicator is not None and latest_indicator.atr14 is not None
                    else 0.0
                ),
            }

            # Quy ước nhãn kết quả giao dịch.
            pnl = float(paper_trade.pnl)
            actual_outcome = 1 if pnl > 0 else 0

            # Ghi feedback theo đúng các trường của model.
            feedback = FeedbackDataset(
                paper_trade_id=paper_trade.id,
                feature_snapshot=features_snapshot,
                predicted_action="BUY",
                actual_outcome=actual_outcome,
            )

            db.add(feedback)
            db.commit()
            db.refresh(feedback)

            logger.info(
                "Feedback created: trade_id=%s, outcome=%s.",
                paper_trade.id,
                actual_outcome,
            )

            return feedback

        except Exception:
            db.rollback()
            logger.exception(
                "Failed to record feedback for trade_id=%s.",
                paper_trade.id,
            )
            raise

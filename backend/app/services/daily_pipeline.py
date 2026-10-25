import logging
from datetime import UTC, datetime
from time import monotonic
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.predictions import predict_stock_signals
from app.core.db import SessionLocal
from app.models.stock import StockPrice, TechnicalIndicator
from app.repositories.indicator_repository import IndicatorRepository
from app.repositories.stock_repository import StockRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.prediction import PredictRequest
from app.services.data_collector import DataCollectorService
from app.services.indicator_service import IndicatorService
from app.services.risk_signal_service import RiskSignalService
from app.services.telegram_service import TelegramService

logger = logging.getLogger(__name__)


def run_daily_quant_pipeline(
    symbols: list[str] | None = None,
    account_risk_limit: float = 500.0,
) -> dict[str, Any]:
    """Thực thi toàn bộ chuỗi Pipeline Định lượng hàng ngày."""
    if symbols is None:
        symbols = ["FPT.VN"]

    start_time = datetime.now(UTC)
    start_monotonic = monotonic()

    logger.info(
        "========== BẮT ĐẦU DAILY QUANT PIPELINE LÚC %s ==========",
        start_time.isoformat(),
    )

    summary: dict[str, Any] = {
        "timestamp": start_time.isoformat(),
        "symbols_processed": [],
        "signals_generated": [],
        "errors": [],
    }

    db: Session = SessionLocal()

    try:
        stock_repo = StockRepository(db)
        indicator_repo = IndicatorRepository(db)
        trade_repo = TradeRepository(db)

        # 1. Thu thập dữ liệu giá OHLCV và validate.
        logger.info("Bước 1: Thu thập giá và validate...")

        for sym in symbols:
            sym_upper = sym.upper()

            try:
                stock_repo.upsert_stock(symbol=sym_upper)

                df_raw = DataCollectorService.fetch_stock_prices(
                    sym_upper,
                    period="1mo",
                )

                cleaned = DataCollectorService.validate_and_clean_prices(
                    df_raw,
                    sym_upper,
                )

                if cleaned:
                    stock_repo.bulk_upsert_stock_prices(cleaned)

                summary["symbols_processed"].append(sym_upper)

            except Exception as exc:
                err_msg = f"Lỗi thu thập giá cho {sym_upper}: {exc!s}"

                logger.exception(
                    "Lỗi thu thập giá cho mã %s",
                    sym_upper,
                )

                summary["errors"].append(err_msg)

        # 2. Tính toán và cập nhật chỉ báo kỹ thuật.
        logger.info("Bước 2: Tính toán chỉ báo kỹ thuật...")

        for sym in summary["symbols_processed"]:
            try:
                prices = indicator_repo.get_prices_by_symbol(sym)

                if prices:
                    ind_records = IndicatorService.calculate_indicators(
                        prices,
                        sym,
                    )

                    if ind_records:
                        indicator_repo.bulk_upsert_indicators(ind_records)

            except Exception as exc:
                err_msg = f"Lỗi tính chỉ báo cho {sym}: {exc!s}"

                logger.exception(
                    "Lỗi tính toán chỉ báo kỹ thuật cho mã %s",
                    sym,
                )

                summary["errors"].append(err_msg)

        # 3. Suy luận Machine Learning và sinh tín hiệu giao dịch.
        logger.info(
            "Bước 3 & 4: Suy luận ML và sinh Tín hiệu/Kế hoạch lệnh..."
        )

        if summary["symbols_processed"]:
            pred_req = PredictRequest(
                symbols=summary["symbols_processed"],
            )

            pred_resp = predict_stock_signals(
                payload=pred_req,
                db=db,
            )

            for pred in pred_resp.predictions:
                sym = pred.symbol

                latest_p = db.scalars(
                    select(StockPrice)
                    .where(StockPrice.symbol == sym)
                    .order_by(StockPrice.date.desc())
                    .limit(1)
                ).first()

                latest_ind = db.scalars(
                    select(TechnicalIndicator)
                    .where(TechnicalIndicator.symbol == sym)
                    .order_by(TechnicalIndicator.date.desc())
                    .limit(1)
                ).first()

                if latest_p is None:
                    logger.warning(
                        "Không tìm thấy dữ liệu giá mới nhất cho mã %s",
                        sym,
                    )
                    continue

                close_p = float(latest_p.close)

                rsi_val = (
                    float(latest_ind.rsi14)
                    if latest_ind is not None
                    and latest_ind.rsi14 is not None
                    else None
                )

                sma20_val = (
                    float(latest_ind.sma20)
                    if latest_ind is not None
                    and latest_ind.sma20 is not None
                    else None
                )

                atr14_val = (
                    float(latest_ind.atr14)
                    if latest_ind is not None
                    and latest_ind.atr14 is not None
                    else None
                )

                sig_info = RiskSignalService.generate_signal(
                    probability_up=pred.probability_up,
                    rsi=rsi_val,
                    close_price=close_p,
                    sma20=sma20_val,
                )

                trade_repo.save_signal(
                    {
                        "symbol": sym,
                        "timestamp": datetime.now(UTC),
                        "action": sig_info["action"],
                        "confidence": sig_info["confidence"],
                        "reasoning": sig_info["reasoning"],
                    }
                )

                plan_dict = None

                if sig_info["action"] == "BUY":
                    plan_dict = RiskSignalService.calculate_trade_plan(
                        symbol=sym,
                        entry_price=close_p,
                        atr14=atr14_val,
                        account_risk_limit=account_risk_limit,
                    )

                    if plan_dict:
                        trade_repo.save_trade_plan(plan_dict)

                summary["signals_generated"].append(
                    {
                        "symbol": sym,
                        "action": sig_info["action"],
                        "confidence": sig_info["confidence"],
                        "trade_plan": plan_dict,
                    }
                )

        # 4. Tổng kết thời gian thực thi pipeline.
        execution_duration = monotonic() - start_monotonic
        summary["duration_seconds"] = round(execution_duration, 2)

        logger.info(
            "========== HOÀN THÀNH PIPELINE TRONG %.2f GIÂY ==========",
            execution_duration,
        )

    except Exception as exc:
        logger.exception("Lỗi nghiêm trọng trong Daily Pipeline")
        summary["errors"].append(str(exc))

    finally:
        db.close()

    # 5. Gửi báo cáo kết quả về Telegram.
    try:
        logger.info("Đang gửi báo cáo kết quả về Telegram Bot...")

        message_content = TelegramService.format_pipeline_summary(summary)

        is_sent = TelegramService.send_message(message_content)

        if is_sent:
            logger.info("Đã gửi báo cáo Telegram thành công.")
        else:
            logger.warning("Không thể gửi báo cáo Telegram.")

    except Exception:
        logger.exception("Lỗi khi gửi thông báo Telegram.")

    return summary
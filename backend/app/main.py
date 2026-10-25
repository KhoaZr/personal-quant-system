# backend/app/main.py

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.indicators import router as indicators_router
from app.api.v1.paper_trades import router as paper_trades_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.stocks import router as stocks_router
from app.api.v1.trades import router as trades_router
from app.services.daily_pipeline import run_daily_quant_pipeline

# ============================================================
# 1. CẤU HÌNH LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# 2. KHỞI TẠO SCHEDULER
# ============================================================

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Quản lý vòng đời ứng dụng FastAPI.
    Tự động chạy Daily Quant Pipeline lúc 23:00 từ thứ Hai đến thứ Sáu.
    """

    # Lập lịch chạy tự động lúc 23:00 từ thứ Hai đến thứ Sáu
    trigger = CronTrigger(
        hour=23,
        minute=0,
        day_of_week="mon-fri",
    )

    scheduler.add_job(
        run_daily_quant_pipeline,
        trigger=trigger,
        id="daily_quant_pipeline_job",
        name="Chạy Daily Quant Pipeline lúc 23:00",
        replace_existing=True,
    )

    scheduler.start()

    logger.info("APScheduler đã khởi động: Daily Pipeline được lên lịch chạy lúc 23:00.")

    yield

    # Dừng scheduler khi ứng dụng tắt
    scheduler.shutdown()

    logger.info("APScheduler đã dừng.")


# ============================================================
# 3. KHỞI TẠO FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Personal Quant System API",
    version="0.1.0",
    description="Backend REST API for Personal Quant System",
    lifespan=lifespan,
)


# ============================================================
# 4. CẤU HÌNH CORS MIDDLEWARE
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 5. ĐĂNG KÝ CÁC API ROUTERS
# ============================================================

app.include_router(stocks_router, prefix="/api/v1")
app.include_router(indicators_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(trades_router, prefix="/api/v1")
app.include_router(paper_trades_router, prefix="/api/v1")


# ============================================================
# 6. API KÍCH HOẠT DAILY PIPELINE THỦ CÔNG
# ============================================================


@app.post(
    "/api/v1/pipeline/trigger-daily",
    tags=["Automation Pipeline"],
)
def trigger_daily_pipeline_manual(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """
    Kích hoạt thủ công Daily Pipeline chạy ngầm,
    không chặn request hiện tại.
    """

    background_tasks.add_task(run_daily_quant_pipeline)

    return {
        "status": "triggered",
        "message": ("Daily Quant Pipeline đã được kích hoạt chạy ngầm thành công."),
    }


# ============================================================
# 7. ROOT ENDPOINT
# ============================================================


@app.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    """Chuyển hướng trang chủ sang tài liệu API."""
    return RedirectResponse(url="/docs")


# ============================================================
# 8. HEALTH CHECK ENDPOINT
# ============================================================


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Kiểm tra trạng thái hoạt động của backend."""

    return {
        "status": "healthy",
        "service": "personal-quant-backend",
    }

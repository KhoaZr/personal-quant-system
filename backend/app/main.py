
# backend/app/main.py

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from zoneinfo import ZoneInfo

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
# 2. CẤU HÌNH TIMEZONE VÀ SCHEDULER
# ============================================================

# Múi giờ Việt Nam (UTC+7)
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

# Khởi tạo Scheduler theo giờ Việt Nam
scheduler = BackgroundScheduler(
    timezone=VN_TZ,
)


# ============================================================
# 3. QUẢN LÝ VÒNG ĐỜI FASTAPI
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Quản lý vòng đời ứng dụng FastAPI.

    Tự động chạy Daily Quant Pipeline:
    - Thời gian: 23:00
    - Múi giờ: Asia/Ho_Chi_Minh
    - Ngày: Thứ Hai đến Thứ Sáu.
    """

    # Tạo lịch chạy tự động
    trigger = CronTrigger(
        hour=23,
        minute=0,
        day_of_week="mon-fri",
        timezone=VN_TZ,
    )

    # Đăng ký công việc
    scheduler.add_job(
        run_daily_quant_pipeline,
        trigger=trigger,
        id="daily_quant_pipeline_job",
        name="Daily Quant Pipeline - 23:00 Vietnam Time",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    # Khởi động Scheduler
    scheduler.start()

    logger.info(
        "APScheduler started: "
        "Daily Pipeline scheduled at 23:00 "
        "(Asia/Ho_Chi_Minh), Monday-Friday."
    )

    try:
        yield

    finally:
        # Tắt Scheduler khi FastAPI shutdown
        scheduler.shutdown(wait=True)

        logger.info("APScheduler stopped.")


# ============================================================
# 4. KHỞI TẠO FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Personal Quant System API",
    version="0.1.0",
    description="Backend REST API for Personal Quant System",
    lifespan=lifespan,
)


# ============================================================
# 5. CẤU HÌNH CORS MIDDLEWARE
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
# 6. ĐĂNG KÝ API ROUTERS
# ============================================================

app.include_router(stocks_router, prefix="/api/v1")
app.include_router(indicators_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(trades_router, prefix="/api/v1")
app.include_router(paper_trades_router, prefix="/api/v1")


# ============================================================
# 7. API KÍCH HOẠT DAILY PIPELINE THỦ CÔNG
# ============================================================

@app.post(
    "/api/v1/pipeline/trigger-daily",
    tags=["Automation Pipeline"],
)
def trigger_daily_pipeline_manual(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """
    Kích hoạt Daily Pipeline thủ công ở background.
    """

    background_tasks.add_task(run_daily_quant_pipeline)

    return {
        "status": "triggered",
        "message": "Daily Quant Pipeline đã được kích hoạt.",
    }


# ============================================================
# 8. ROOT ENDPOINT
# ============================================================

@app.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    """Chuyển hướng sang API Documentation."""

    return RedirectResponse(url="/docs")


# ============================================================
# 9. HEALTH CHECK ENDPOINT
# ============================================================

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Kiểm tra trạng thái Backend."""

    return {
        "status": "healthy",
        "service": "personal-quant-backend",
    }

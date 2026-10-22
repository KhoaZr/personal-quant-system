from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.v1.indicators import router as indicators_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.stocks import router as stocks_router
from app.api.v1.trades import router as trades_router
from app.api.v1.paper_trades import router as paper_trades_router

app = FastAPI(
    title="Personal Quant System API",
    version="0.1.0",
    description="Backend REST API for Personal Quant System",
)

# Register Routers
app.include_router(stocks_router, prefix="/api/v1")
app.include_router(indicators_router, prefix="/api/v1")
app.include_router(predictions_router, prefix="/api/v1")
app.include_router(trades_router, prefix="/api/v1")
app.include_router(paper_trades_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "personal-quant-backend",
    }

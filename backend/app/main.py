from fastapi import FastAPI

from app.api.v1.stocks import router as stocks_router

app = FastAPI(
    title="Personal Quant System API",
    version="0.1.0",
    description="Backend REST API for Personal Quant System",
)


app.include_router(
    stocks_router,
    prefix="/api/v1",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "personal-quant-backend",
    }

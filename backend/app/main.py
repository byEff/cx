from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config import settings
from app.database import init_db
from app.api.v1 import stocks, watchlist, alerts, market, industry, etf, portfolio

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting up application...")
    await init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(
    stocks.router, prefix=f"{settings.API_PREFIX}/stocks", tags=["Stocks"]
)
app.include_router(
    watchlist.router, prefix=f"{settings.API_PREFIX}/watchlist", tags=["Watchlist"]
)
app.include_router(
    alerts.router, prefix=f"{settings.API_PREFIX}/alerts", tags=["Alerts"]
)
app.include_router(
    market.router, prefix=f"{settings.API_PREFIX}/market", tags=["Market"]
)
app.include_router(
    industry.router, prefix=f"{settings.API_PREFIX}/market", tags=["Industry"]
)
app.include_router(
    etf.router, prefix=f"{settings.API_PREFIX}/etf", tags=["ETF"]
)
app.include_router(
    portfolio.router, prefix=f"{settings.API_PREFIX}/portfolio", tags=["Portfolio"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.BACKEND_DEBUG,
    )

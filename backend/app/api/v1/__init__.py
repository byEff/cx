from .stocks import router as stocks_router
from .watchlist import router as watchlist_router
from .alerts import router as alerts_router
from .market import router as market_router
from .industry import router as industry_router

__all__ = [
    "stocks_router",
    "watchlist_router",
    "alerts_router",
    "market_router",
    "industry_router",
]

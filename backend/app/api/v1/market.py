from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.models import MarketNews
from app.models.schemas import (
    MarketNewsResponse,
    StockSearchResult,
    UpDownDistribution,
    LimitUpStats,
)
from app.services.stock_data import StockDataService
from app.services.data_sources.market_sentiment import get_market_sentiment_source
from loguru import logger

router = APIRouter()


@router.get("/news", response_model=List[MarketNewsResponse])
async def get_market_news(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取市场资讯"""
    try:
        result = await db.execute(
            select(MarketNews).order_by(MarketNews.news_time.desc()).limit(limit)
        )
        news = result.scalars().all()
        return news
    except Exception as e:
        logger.error(f"Error getting market news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index", response_model=List[StockSearchResult])
async def get_market_index(db: AsyncSession = Depends(get_db)):
    """获取大盘指数"""
    try:
        stock_service = StockDataService()
        indices = await stock_service.get_market_indices()
        return indices
    except Exception as e:
        logger.error(f"Error getting market indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-gainers", response_model=List[StockSearchResult])
async def get_top_gainers(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取涨幅榜"""
    try:
        stock_service = StockDataService()
        gainers = await stock_service.get_top_gainers(limit)
        return gainers
    except Exception as e:
        logger.error(f"Error getting top gainers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-losers", response_model=List[StockSearchResult])
async def get_top_losers(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """获取跌幅榜"""
    try:
        stock_service = StockDataService()
        losers = await stock_service.get_top_losers(limit)
        return losers
    except Exception as e:
        logger.error(f"Error getting top losers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-sectors")
async def get_hot_sectors(db: AsyncSession = Depends(get_db)):
    """获取热门板块"""
    try:
        stock_service = StockDataService()
        sectors = await stock_service.get_hot_sectors()
        return sectors
    except Exception as e:
        logger.error(f"Error getting hot sectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 市场情绪接口 ====================

@router.get("/up-down-distribution", response_model=UpDownDistribution)
async def get_up_down_distribution():
    """获取涨跌家数分布"""
    try:
        sentiment_source = get_market_sentiment_source()
        data = await sentiment_source.get_up_down_distribution()
        return UpDownDistribution(**data)
    except Exception as e:
        logger.error(f"Error getting up-down distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/limit-up-stats", response_model=LimitUpStats)
async def get_limit_up_stats():
    """获取涨停板统计"""
    try:
        sentiment_source = get_market_sentiment_source()
        data = await sentiment_source.get_limit_up_stats()
        return LimitUpStats(**data)
    except Exception as e:
        logger.error(f"Error getting limit-up stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot-stocks", response_model=List[StockSearchResult])
async def get_hot_stocks(
    limit: int = Query(20, ge=1, le=50)
):
    """获取热门股票榜单"""
    try:
        sentiment_source = get_market_sentiment_source()
        stocks = await sentiment_source.get_hot_stocks(limit)
        return stocks
    except Exception as e:
        logger.error(f"Error getting hot stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

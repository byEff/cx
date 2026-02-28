from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.models import MarketNews
from app.models.schemas import MarketNewsResponse, StockSearchResult
from app.services.stock_data import StockDataService
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

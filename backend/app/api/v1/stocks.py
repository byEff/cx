from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db
from app.models.schemas import (
    StockResponse,
    StockQuoteResponse,
    KlineData,
    StockSearchResult,
    TechnicalIndicators,
)
from app.services.stock_data import StockDataService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.data_sources.eastmoney import EastMoneyDataSource
from loguru import logger

router = APIRouter()


@router.get("/realtime", response_model=List[StockQuoteResponse])
async def get_realtime_quotes(
    codes: Optional[str] = Query(None, description="股票代码，逗号分隔"),
    db: AsyncSession = Depends(get_db),
):
    """获取实时行情数据"""
    try:
        stock_service = StockDataService()
        if codes:
            code_list = [code.strip() for code in codes.split(",")]
        else:
            code_list = []

        quotes = await stock_service.get_realtime_quotes(code_list)
        return quotes
    except Exception as e:
        logger.error(f"Error getting realtime quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/quote", response_model=StockQuoteResponse)
async def get_stock_quote(code: str, db: AsyncSession = Depends(get_db)):
    """获取单只股票实时行情"""
    try:
        stock_service = StockDataService()
        quote = await stock_service.get_stock_quote(code)
        if not quote:
            raise HTTPException(status_code=404, detail="Stock not found")
        return quote
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stock quote for {code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/kline", response_model=List[KlineData])
async def get_kline_data(
    code: str,
    period: str = Query("day", pattern="^(day|week|month|minute)$"),
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """获取K线数据"""
    try:
        stock_service = StockDataService()
        kline_data = await stock_service.get_kline_data(code, period, limit)
        return kline_data
    except Exception as e:
        logger.error(f"Error getting kline data for {code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[StockSearchResult])
async def search_stocks(
    keyword: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)
):
    """搜索股票"""
    try:
        stock_service = StockDataService()
        results = await stock_service.search_stocks(keyword)
        return results
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter", response_model=List[StockSearchResult])
async def filter_stocks(
    industry: Optional[str] = None,
    min_change: Optional[float] = None,
    max_change: Optional[float] = None,
    min_volume: Optional[int] = None,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """筛选股票"""
    try:
        stock_service = StockDataService()
        results = await stock_service.filter_stocks(
            industry, min_change, max_change, min_volume, limit
        )
        return results
    except Exception as e:
        logger.error(f"Error filtering stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/analysis", response_model=TechnicalIndicators)
async def get_technical_analysis(code: str, db: AsyncSession = Depends(get_db)):
    """获取技术指标分析"""
    try:
        ta_service = TechnicalAnalysisService()
        indicators = await ta_service.calculate_indicators(code)
        return indicators
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 高级筛选接口 ====================


@router.get("/limit-up", response_model=List[StockSearchResult])
async def get_limit_up_stocks(limit: int = Query(50, ge=1, le=200)):
    """获取涨停板列表"""
    try:
        eastmoney = EastMoneyDataSource()
        stocks = await eastmoney.get_limit_up_stocks(limit)
        return stocks
    except Exception as e:
        logger.error(f"Error getting limit-up stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/limit-down", response_model=List[StockSearchResult])
async def get_limit_down_stocks(limit: int = Query(50, ge=1, le=200)):
    """获取跌停板列表"""
    try:
        eastmoney = EastMoneyDataSource()
        stocks = await eastmoney.get_limit_down_stocks(limit)
        return stocks
    except Exception as e:
        logger.error(f"Error getting limit-down stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/new-listing", response_model=List[StockSearchResult])
async def get_new_stocks(limit: int = Query(50, ge=1, le=200)):
    """获取次新股列表"""
    try:
        eastmoney = EastMoneyDataSource()
        stocks = await eastmoney.get_new_stocks(limit)
        return stocks
    except Exception as e:
        logger.error(f"Error getting new stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kcb", response_model=List[StockSearchResult])
async def get_kcb_stocks(limit: int = Query(50, ge=1, le=200)):
    """获取科创板列表"""
    try:
        eastmoney = EastMoneyDataSource()
        stocks = await eastmoney.get_kcb_stocks(limit)
        return stocks
    except Exception as e:
        logger.error(f"Error getting kcb stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cyb", response_model=List[StockSearchResult])
async def get_cyb_stocks(limit: int = Query(50, ge=1, le=200)):
    """获取创业板列表"""
    try:
        eastmoney = EastMoneyDataSource()
        stocks = await eastmoney.get_cyb_stocks(limit)
        return stocks
    except Exception as e:
        logger.error(f"Error getting cyb stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

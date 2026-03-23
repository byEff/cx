"""
ETF API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.schemas import ETFResponse, ETFQuoteResponse
from app.services.data_sources.etf import get_etf_source
from loguru import logger

router = APIRouter()


@router.get("/list", response_model=List[ETFResponse])
async def get_etf_list(
    limit: int = Query(100, ge=1, le=500),
    etf_type: Optional[str] = Query(None, description="ETF类型: 股票型, 债券型, 货币型, QDII, 商品型")
):
    """获取ETF列表

    Args:
        limit: 返回数量限制
        etf_type: ETF类型筛选
    """
    try:
        etf_source = get_etf_source()
        etf_list = await etf_source.get_etf_list(limit, etf_type)
        return [ETFResponse(**etf.model_dump()) for etf in etf_list]
    except Exception as e:
        logger.error(f"Error getting ETF list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}/quote", response_model=ETFQuoteResponse)
async def get_etf_quote(code: str):
    """获取ETF实时行情

    Args:
        code: ETF代码
    """
    try:
        etf_source = get_etf_source()
        quote = await etf_source.get_etf_quote(code)
        if not quote:
            raise HTTPException(status_code=404, detail="ETF not found")
        return ETFQuoteResponse(**quote.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ETF quote for {code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quotes", response_model=List[ETFQuoteResponse])
async def get_etf_quotes(
    codes: str = Query(..., description="ETF代码，逗号分隔")
):
    """批量获取ETF行情

    Args:
        codes: ETF代码，逗号分隔
    """
    try:
        code_list = [c.strip() for c in codes.split(",") if c.strip()]
        if not code_list:
            raise HTTPException(status_code=400, detail="请提供ETF代码")

        etf_source = get_etf_source()
        quotes = await etf_source.get_etf_quotes(code_list)
        return [ETFQuoteResponse(**q.model_dump()) for q in quotes]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ETF quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
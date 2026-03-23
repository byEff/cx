from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.services.data_sources.industry import IndustryDataSource
from loguru import logger

router = APIRouter()


@router.get("/industries", response_model=Dict[str, Any])
async def get_industries(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=10, le=200),
    sort_by: str = Query(
        "change_percent",
        pattern="^(change_percent|change_5d|change_ytd|turnover|volume)$",
    ),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """获取行业列表（支持分页）"""
    try:
        industry_ds = IndustryDataSource()
        # 获取所有行业数据
        all_industries = await industry_ds.get_industry_list(500)

        # 排序
        if all_industries:
            reverse = order == "desc"
            all_industries.sort(key=lambda x: x.get(sort_by, 0) or 0, reverse=reverse)

        # 分页
        total = len(all_industries)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_industries = all_industries[start:end]

        # 添加分页信息
        return {
            "data": paginated_industries,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }
    except Exception as e:
        logger.error(f"Error getting industries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industries/{code}/stocks", response_model=List[dict])
async def get_industry_stocks(code: str, db: AsyncSession = Depends(get_db)):
    """获取板块内股票列表"""
    try:
        industry_ds = IndustryDataSource()
        stocks = await industry_ds.get_board_stocks(code, 200)
        return stocks
    except Exception as e:
        logger.error(f"Error getting industry stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from app.database import get_db
from app.models.models import WatchlistItem, Stock
from app.models.schemas import WatchlistCreate, WatchlistResponse
from app.services.stock_data import StockDataService
from loguru import logger

router = APIRouter()


@router.get("", response_model=List[WatchlistResponse])
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    """获取自选股列表"""
    try:
        result = await db.execute(
            select(WatchlistItem).where(WatchlistItem.user_id == 1).order_by(WatchlistItem.created_at.desc())
        )
        items = result.scalars().all()
        return items
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=WatchlistResponse)
async def add_to_watchlist(
    item: WatchlistCreate,
    db: AsyncSession = Depends(get_db)
):
    """添加到自选股"""
    try:
        existing = await db.execute(
            select(WatchlistItem).where(
                and_(
                    WatchlistItem.stock_code == item.stock_code,
                    WatchlistItem.user_id == 1
                )
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Stock already in watchlist")
        
        stock_service = StockDataService()
        current_price = await stock_service.get_current_price(item.stock_code)
        
        watchlist_item = WatchlistItem(
            stock_code=item.stock_code,
            user_id=1,
            add_price=item.add_price or current_price
        )
        db.add(watchlist_item)
        await db.commit()
        await db.refresh(watchlist_item)
        
        return watchlist_item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
async def remove_from_watchlist(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """从自选股删除"""
    try:
        result = await db.execute(
            select(WatchlistItem).where(WatchlistItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        
        await db.delete(item)
        await db.commit()
        
        return {"message": "Removed from watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

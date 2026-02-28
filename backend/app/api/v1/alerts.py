from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.models import PriceAlert
from app.models.schemas import AlertCreate, AlertResponse
from loguru import logger

router = APIRouter()


@router.get("", response_model=List[AlertResponse])
async def get_alerts(db: AsyncSession = Depends(get_db)):
    """获取预警列表"""
    try:
        result = await db.execute(
            select(PriceAlert).order_by(PriceAlert.created_at.desc())
        )
        alerts = result.scalars().all()
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建价格预警"""
    try:
        if alert.alert_type not in ["price_up", "price_down", "change_up", "change_down"]:
            raise HTTPException(status_code=400, detail="Invalid alert type")
        
        new_alert = PriceAlert(
            stock_code=alert.stock_code,
            alert_type=alert.alert_type,
            threshold=alert.threshold,
            is_active=True
        )
        db.add(new_alert)
        await db.commit()
        await db.refresh(new_alert)
        
        return new_alert
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{alert_id}/deactivate")
async def deactivate_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """停用预警"""
    try:
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert.is_active = False
        await db.commit()
        
        return {"message": "Alert deactivated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除预警"""
    try:
        result = await db.execute(
            select(PriceAlert).where(PriceAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        await db.delete(alert)
        await db.commit()
        
        return {"message": "Alert deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

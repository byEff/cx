"""
持仓管理API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from decimal import Decimal
from app.database import get_db
from app.models.portfolio import PortfolioGroup, Position
from app.models.schemas import (
    PortfolioGroupCreate,
    PortfolioGroupResponse,
    PositionCreate,
    PositionUpdate,
    PositionResponse,
    ProfitLossSummary,
    ProfitLossItem,
)
from app.services.data_sources.manager import get_data_source_manager
from loguru import logger

router = APIRouter()


# ==================== 分组管理 ====================

@router.post("/groups", response_model=PortfolioGroupResponse)
async def create_group(
    group: PortfolioGroupCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建持仓分组"""
    try:
        new_group = PortfolioGroup(
            name=group.name,
            user_id=1  # 默认用户
        )
        db.add(new_group)
        await db.flush()
        await db.refresh(new_group)
        return new_group
    except Exception as e:
        logger.error(f"创建分组失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/groups", response_model=List[PortfolioGroupResponse])
async def get_groups(db: AsyncSession = Depends(get_db)):
    """获取分组列表"""
    try:
        result = await db.execute(
            select(PortfolioGroup).where(PortfolioGroup.user_id == 1)
        )
        groups = result.scalars().all()
        return groups
    except Exception as e:
        logger.error(f"获取分组失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/groups/{group_id}", response_model=PortfolioGroupResponse)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个分组"""
    try:
        result = await db.execute(
            select(PortfolioGroup).where(PortfolioGroup.id == group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="分组不存在")
        return group
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分组失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/groups/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    """删除分组（同时删除分组下的所有持仓）"""
    try:
        result = await db.execute(
            select(PortfolioGroup).where(PortfolioGroup.id == group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="分组不存在")

        await db.delete(group)
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除分组失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 持仓管理 ====================

@router.post("/positions", response_model=PositionResponse)
async def create_position(
    position: PositionCreate,
    db: AsyncSession = Depends(get_db)
):
    """添加持仓"""
    try:
        # 检查分组是否存在
        result = await db.execute(
            select(PortfolioGroup).where(PortfolioGroup.id == position.group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="分组不存在")

        # 获取股票名称（如果没有提供）
        stock_name = position.stock_name
        if not stock_name:
            try:
                ds_manager = get_data_source_manager()
                quotes = await ds_manager.get_quotes([position.stock_code])
                if quotes:
                    # 需要从其他接口获取名称
                    pass
            except Exception:
                pass

        new_position = Position(
            group_id=position.group_id,
            stock_code=position.stock_code,
            stock_name=stock_name or position.stock_code,
            cost_price=position.cost_price,
            quantity=position.quantity
        )
        db.add(new_position)
        await db.flush()
        await db.refresh(new_position)
        return new_position
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加持仓失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    group_id: int = Query(None, description="分组ID，不传则返回所有"),
    db: AsyncSession = Depends(get_db)
):
    """获取持仓列表"""
    try:
        query = select(Position)
        if group_id:
            query = query.where(Position.group_id == group_id)

        result = await db.execute(query)
        positions = result.scalars().all()
        return positions
    except Exception as e:
        logger.error(f"获取持仓失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions/{position_id}", response_model=PositionResponse)
async def get_position(position_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个持仓"""
    try:
        result = await db.execute(
            select(Position).where(Position.id == position_id)
        )
        position = result.scalar_one_or_none()
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")
        return position
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取持仓失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/positions/{position_id}", response_model=PositionResponse)
async def update_position(
    position_id: int,
    update_data: PositionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新持仓"""
    try:
        result = await db.execute(
            select(Position).where(Position.id == position_id)
        )
        position = result.scalar_one_or_none()
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")

        if update_data.cost_price is not None:
            position.cost_price = update_data.cost_price
        if update_data.quantity is not None:
            position.quantity = update_data.quantity

        await db.flush()
        await db.refresh(position)
        return position
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新持仓失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/positions/{position_id}")
async def delete_position(position_id: int, db: AsyncSession = Depends(get_db)):
    """删除持仓"""
    try:
        result = await db.execute(
            select(Position).where(Position.id == position_id)
        )
        position = result.scalar_one_or_none()
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")

        await db.delete(position)
        return {"message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除持仓失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 盈亏计算 ====================

@router.get("/profit-loss", response_model=ProfitLossSummary)
async def calculate_profit_loss(
    group_id: int = Query(None, description="分组ID，不传则计算所有"),
    db: AsyncSession = Depends(get_db)
):
    """计算实时盈亏"""
    try:
        # 获取持仓
        query = select(Position)
        if group_id:
            query = query.where(Position.group_id == group_id)

        result = await db.execute(query)
        positions = result.scalars().all()

        if not positions:
            return ProfitLossSummary(
                total_cost=Decimal("0"),
                total_market_value=Decimal("0"),
                total_profit_loss=Decimal("0"),
                total_profit_loss_percent=Decimal("0"),
                positions=[]
            )

        # 获取实时行情
        stock_codes = [p.stock_code for p in positions]
        ds_manager = get_data_source_manager()
        quotes = await ds_manager.get_quotes(stock_codes)

        # 构建行情字典
        quote_dict = {q.stock_code: q for q in quotes}

        # 计算盈亏
        total_cost = Decimal("0")
        total_market_value = Decimal("0")
        profit_loss_items = []

        for pos in positions:
            cost = pos.cost_price * pos.quantity
            total_cost += cost

            quote = quote_dict.get(pos.stock_code)
            item = ProfitLossItem(
                position_id=pos.id,
                stock_code=pos.stock_code,
                stock_name=pos.stock_name,
                quantity=pos.quantity,
                cost_price=pos.cost_price,
            )

            if quote and quote.price:
                market_value = quote.price * pos.quantity
                profit_loss = market_value - cost
                profit_loss_percent = (profit_loss / cost * 100) if cost > 0 else Decimal("0")

                item.current_price = quote.price
                item.market_value = market_value
                item.profit_loss = profit_loss
                item.profit_loss_percent = profit_loss_percent

                total_market_value += market_value

            profit_loss_items.append(item)

        # 汇总
        total_profit_loss = total_market_value - total_cost
        total_profit_loss_percent = (
            total_profit_loss / total_cost * 100
            if total_cost > 0
            else Decimal("0")
        )

        return ProfitLossSummary(
            total_cost=total_cost,
            total_market_value=total_market_value,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percent=total_profit_loss_percent,
            positions=profit_loss_items
        )

    except Exception as e:
        logger.error(f"计算盈亏失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
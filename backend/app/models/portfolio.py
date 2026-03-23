"""
持仓管理模型
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PortfolioGroup(Base):
    """持仓分组"""
    __tablename__ = "portfolio_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, default=1)  # 暂时使用默认用户
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联持仓
    positions = relationship("Position", back_populates="group", cascade="all, delete-orphan")


class Position(Base):
    """持仓记录"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("portfolio_groups.id"), nullable=False, index=True)
    stock_code = Column(String(10), nullable=False, index=True)
    stock_name = Column(String(50))  # 冗余存储股票名称
    cost_price = Column(Numeric(10, 3), nullable=False)  # 成本价（精确到3位小数）
    quantity = Column(Integer, nullable=False)  # 持仓量（股数）
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联分组
    group = relationship("PortfolioGroup", back_populates="positions")
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class StockBase(BaseModel):
    code: str
    name: str
    industry: Optional[str] = None
    market: Optional[str] = None


class StockResponse(StockBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockQuoteBase(BaseModel):
    stock_code: str
    stock_name: Optional[str] = None
    price: Decimal
    open_price: Optional[Decimal] = None
    high_price: Optional[Decimal] = None
    low_price: Optional[Decimal] = None
    pre_close: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[int] = None
    turnover: Optional[Decimal] = None
    timestamp: datetime


class StockQuoteResponse(StockQuoteBase):
    id: int

    class Config:
        from_attributes = True


class KlineData(BaseModel):
    time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


class WatchlistCreate(BaseModel):
    stock_code: str
    add_price: Optional[Decimal] = None


class WatchlistResponse(BaseModel):
    id: int
    stock_code: str
    add_price: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    stock_code: str
    alert_type: str
    threshold: Decimal


class AlertResponse(BaseModel):
    id: int
    stock_code: str
    alert_type: str
    threshold: Decimal
    is_active: bool
    triggered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MarketNewsResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    source: Optional[str] = None
    news_time: Optional[datetime] = None
    url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StockSearchResult(BaseModel):
    code: str
    name: str
    price: Optional[Decimal] = Field(default=None, serialization_alias="price")
    change_percent: Optional[Decimal] = Field(
        default=None, serialization_alias="changePercent"
    )
    volume: Optional[int] = Field(default=None, serialization_alias="volume")
    turnover: Optional[Decimal] = Field(default=None, serialization_alias="turnover")
    turnover_rate: Optional[Decimal] = Field(
        default=None, serialization_alias="turnoverRate"
    )
    amplitude: Optional[Decimal] = Field(default=None, serialization_alias="amplitude")
    pe_ratio: Optional[Decimal] = Field(default=None, serialization_alias="peRatio")
    total_market_value: Optional[Decimal] = Field(
        default=None, serialization_alias="totalMarketValue"
    )
    industry: Optional[str] = Field(default=None, serialization_alias="industry")
    market: Optional[str] = Field(default=None, serialization_alias="market")

    model_config = {"populate_by_name": True}


class TechnicalIndicators(BaseModel):
    ma5: Optional[Decimal] = None
    ma10: Optional[Decimal] = None
    ma20: Optional[Decimal] = None
    macd: Optional[Decimal] = None
    macd_signal: Optional[Decimal] = None
    macd_hist: Optional[Decimal] = None
    rsi: Optional[Decimal] = None
    kdj_k: Optional[Decimal] = None
    kdj_d: Optional[Decimal] = None
    kdj_j: Optional[Decimal] = None


# Portfolio schemas
class PortfolioGroupCreate(BaseModel):
    name: str


class PortfolioGroupResponse(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PositionCreate(BaseModel):
    group_id: int
    stock_code: str
    stock_name: Optional[str] = None
    cost_price: Decimal
    quantity: int


class PositionUpdate(BaseModel):
    cost_price: Optional[Decimal] = None
    quantity: Optional[int] = None


class PositionResponse(BaseModel):
    id: int
    group_id: int
    stock_code: str
    stock_name: Optional[str] = None
    cost_price: Decimal
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProfitLossItem(BaseModel):
    """盈亏计算结果"""

    position_id: int
    stock_code: str
    stock_name: Optional[str] = None
    quantity: int
    cost_price: Decimal
    current_price: Optional[Decimal] = None
    market_value: Optional[Decimal] = None
    profit_loss: Optional[Decimal] = None
    profit_loss_percent: Optional[Decimal] = None


class ProfitLossSummary(BaseModel):
    """盈亏汇总"""

    total_cost: Decimal
    total_market_value: Optional[Decimal] = None
    total_profit_loss: Optional[Decimal] = None
    total_profit_loss_percent: Optional[Decimal] = None
    positions: List[ProfitLossItem]


# Market Sentiment schemas
class UpDownDistribution(BaseModel):
    """涨跌分布"""

    up_count: int = Field(serialization_alias="upCount")
    down_count: int = Field(serialization_alias="downCount")
    flat_count: int = Field(serialization_alias="flatCount")
    limit_up: int = Field(serialization_alias="limitUp")
    limit_down: int = Field(serialization_alias="limitDown")
    up_limit_count: Optional[int] = Field(
        default=None, serialization_alias="upLimitCount"
    )
    down_limit_count: Optional[int] = Field(
        default=None, serialization_alias="downLimitCount"
    )
    timestamp: str

    model_config = {"populate_by_name": True}


class LimitUpStats(BaseModel):
    """涨停统计"""

    total_count: int = Field(serialization_alias="totalCount")
    seal_count: int = Field(serialization_alias="sealCount")
    open_count: int = Field(serialization_alias="openCount")
    time_distribution: Optional[dict] = Field(
        default=None, serialization_alias="timeDistribution"
    )
    board_distribution: Optional[dict] = Field(
        default=None, serialization_alias="boardDistribution"
    )
    timestamp: str

    model_config = {"populate_by_name": True}


# ETF schemas
class ETFResponse(BaseModel):
    """ETF数据响应"""

    code: str
    name: str
    price: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[int] = None
    turnover: Optional[Decimal] = None
    market: Optional[str] = None
    type: Optional[str] = None


class ETFQuoteResponse(BaseModel):
    """ETF行情响应"""

    code: str
    name: str
    price: Decimal
    open_price: Optional[Decimal] = None
    high_price: Optional[Decimal] = None
    low_price: Optional[Decimal] = None
    pre_close: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[int] = None
    turnover: Optional[Decimal] = None
    timestamp: datetime

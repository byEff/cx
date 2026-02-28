from pydantic import BaseModel
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
    price: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    industry: Optional[str] = None
    market: Optional[str] = None


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

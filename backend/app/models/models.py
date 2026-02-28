from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, BigInteger, Text
from sqlalchemy.sql import func
from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"
    
    code = Column(String(10), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    industry = Column(String(50))
    market = Column(String(20))
    list_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class WatchlistItem(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), nullable=False, index=True)
    user_id = Column(Integer, default=1)
    add_price = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), nullable=False, index=True)
    alert_type = Column(String(20), nullable=False)
    threshold = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class StockQuote(Base):
    __tablename__ = "stock_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(10), nullable=False, index=True)
    price = Column(Numeric(10, 2))
    open_price = Column(Numeric(10, 2))
    high_price = Column(Numeric(10, 2))
    low_price = Column(Numeric(10, 2))
    pre_close = Column(Numeric(10, 2))
    change_percent = Column(Numeric(10, 2))
    volume = Column(BigInteger)
    turnover = Column(Numeric(20, 2))
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())


class MarketNews(Base):
    __tablename__ = "market_news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    source = Column(String(50))
    news_time = Column(DateTime)
    url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

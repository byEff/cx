"""
数据源抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult


class BaseDataSource(ABC):
    """数据源基类"""

    @abstractmethod
    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取单只股票行情"""
        pass

    @abstractmethod
    async def get_quotes(self, codes: List[str]) -> List[StockQuoteResponse]:
        """批量获取股票行情"""
        pass

    @abstractmethod
    async def get_kline(
        self, code: str, period: str = "day", limit: int = 200
    ) -> List[KlineData]:
        """获取K线数据"""
        pass

    @abstractmethod
    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票"""
        pass

    @abstractmethod
    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表"""
        pass

    @abstractmethod
    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        """获取指数"""
        pass

    @abstractmethod
    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取涨幅榜"""
        pass

    @abstractmethod
    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取跌幅榜"""
        pass

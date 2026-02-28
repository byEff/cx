"""
股票数据服务 - 支持多数据源切换
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger
from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from app.services.data_sources.manager import get_data_source_manager


class StockDataService:
    """股票数据服务"""

    def __init__(self):
        self.ds_manager = get_data_source_manager()

    async def get_stock_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取单只股票行情"""
        return await self.ds_manager.get_quote(code)

    async def get_realtime_quotes(
        self, codes: List[str] = None
    ) -> List[StockQuoteResponse]:
        if not codes:
            codes = self._get_default_codes()

        results = []
        for code in codes[:50]:
            quote = await self.get_stock_quote(code)
            if quote:
                results.append(quote)
        return results

    async def get_kline_data(
        self, code: str, period: str = "day", limit: int = 200
    ) -> List[KlineData]:
        """获取K线数据"""
        return await self.ds_manager.get_kline(code, period, limit)

    async def search_stocks(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票"""
        return await self.ds_manager.search(keyword)

    async def filter_stocks(
        self, industry=None, min_change=None, max_change=None, min_volume=None, limit=50
    ) -> List[StockSearchResult]:
        return await self.ds_manager.get_stock_list(industry, limit)

    async def get_market_indices(self) -> List[StockSearchResult]:
        # 获取大盘指数，使用专门的方法获取真实指数数据
        indices = ["000001", "399001", "399006"]
        results = []
        for code in indices:
            result = await self.ds_manager.get_index(code)
            if result:
                results.append(result)
        return results

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        return await self.ds_manager.get_top_gainers(limit)

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        return await self.ds_manager.get_top_losers(limit)

    async def get_hot_sectors(self) -> List[dict]:
        return []

    async def get_current_price(self, code: str) -> Optional[Decimal]:
        quote = await self.get_stock_quote(code)
        return quote.price if quote else None

    def _get_default_codes(self) -> List[str]:
        return ["000001", "000002", "600000", "600036", "000858"]

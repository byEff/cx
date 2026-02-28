"""
备用数据源 - 本地默认数据
当外部API不可用时使用
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import random

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class LocalDataSource(BaseDataSource):
    """本地默认数据源 - 备用方案"""

    # 常用股票数据缓存
    STOCKS_DB = {
        "000001": {"name": "平安银行", "price": 10.50},
        "000002": {"name": "万科A", "price": 30.25},
        "000651": {"name": "格力电器", "price": 45.80},
        "000858": {"name": "五粮液", "price": 280.00},
        "600000": {"name": "浦发银行", "price": 15.80},
        "600036": {"name": "招商银行", "price": 45.60},
        "600519": {"name": "贵州茅台", "price": 1850.00},
        "601318": {"name": "中国平安", "price": 52.30},
        "601888": {"name": "中国中免", "price": 285.00},
        "603259": {"name": "药明康德", "price": 95.50},
    }

    INDICES_DB = {
        "000001": {"name": "上证指数", "price": 3050.00},
        "399001": {"name": "深证成指", "price": 9850.00},
        "399006": {"name": "创业板指", "price": 1920.00},
    }

    def __init__(self):
        pass

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取股票行情"""
        stock = self.STOCKS_DB.get(code)
        if not stock:
            # 动态生成数据
            stock = {"name": f"股票{code}", "price": 10.0 + random.random() * 100}

        change = (random.random() - 0.5) * 10
        price = round(stock["price"] * (1 + change / 100), 2)

        return StockQuoteResponse(
            id=0,
            stock_code=code,
            price=Decimal(str(price)),
            open_price=Decimal(
                str(round(stock["price"] * (1 + (random.random() - 0.5) * 0.02), 2))
            ),
            high_price=Decimal(str(round(price * 1.02, 2))),
            low_price=Decimal(str(round(price * 0.98, 2))),
            pre_close=Decimal(str(stock["price"])),
            change_percent=Decimal(str(round(change, 2))),
            volume=random.randint(1000000, 100000000),
            turnover=Decimal(
                str(round(price * random.randint(1000000, 100000000) / 10000, 2))
            ),
            timestamp=datetime.now(),
        )

    async def get_quotes(self, codes: List[str]) -> List[StockQuoteResponse]:
        results = []
        for code in codes:
            quote = await self.get_quote(code)
            if quote:
                results.append(quote)
        return results

    async def get_kline(
        self, code: str, period: str = "day", limit: int = 200
    ) -> List[KlineData]:
        """获取K线数据"""
        stock = self.STOCKS_DB.get(code, {"price": 10.0})
        base_price = stock["price"]

        klines = []
        current_time = datetime.now()

        for i in range(min(limit, 30)):
            open_p = base_price * (1 + (random.random() - 0.5) * 0.1)
            close_p = open_p * (1 + (random.random() - 0.5) * 0.1)
            high_p = max(open_p, close_p) * (1 + random.random() * 0.02)
            low_p = min(open_p, close_p) * (1 - random.random() * 0.02)

            klines.append(
                KlineData(
                    time=int((current_time.timestamp()) - i * 86400),
                    open=Decimal(str(round(open_p, 2))),
                    high=Decimal(str(round(high_p, 2))),
                    low=Decimal(str(round(low_p, 2))),
                    close=Decimal(str(round(close_p, 2))),
                    volume=random.randint(1000000, 100000000),
                )
            )

        return list(reversed(klines))

    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票"""
        keyword_lower = keyword.lower()
        results = []

        for code, info in self.STOCKS_DB.items():
            if keyword_lower in code.lower() or keyword_lower in info["name"].lower():
                quote = await self.get_quote(code)
                results.append(
                    StockSearchResult(
                        code=code,
                        name=info["name"],
                        price=quote.price if quote else None,
                        change_percent=quote.change_percent if quote else None,
                        market="SZ" if code.startswith(("0", "3")) else "SH",
                    )
                )

        return results

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        results = []
        for code, info in list(self.STOCKS_DB.items())[:limit]:
            quote = await self.get_quote(code)
            results.append(
                StockSearchResult(
                    code=code,
                    name=info["name"],
                    price=quote.price if quote else None,
                    change_percent=quote.change_percent if quote else None,
                    market="SZ" if code.startswith(("0", "3")) else "SH",
                )
            )
        return results

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        index = self.INDICES_DB.get(code)
        if not index:
            return None

        quote = await self.get_quote(code)
        change = random.uniform(-3, 3)

        return StockSearchResult(
            code=code,
            name=index["name"],
            price=Decimal(str(round(index["price"] * (1 + change / 100), 2))),
            change_percent=Decimal(str(round(change, 2))),
        )

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        results = []
        codes = list(self.STOCKS_DB.keys())[:limit]

        for code in codes:
            quote = await self.get_quote(code)
            if quote and quote.change_percent and quote.change_percent > 0:
                results.append(
                    StockSearchResult(
                        code=code,
                        name=self.STOCKS_DB[code]["name"],
                        price=quote.price,
                        change_percent=quote.change_percent,
                    )
                )

        results.sort(key=lambda x: float(x.change_percent or 0), reverse=True)
        return results[:limit]

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        results = []
        codes = list(self.STOCKS_DB.keys())[:limit]

        for code in codes:
            quote = await self.get_quote(code)
            if quote and quote.change_percent and quote.change_percent < 0:
                results.append(
                    StockSearchResult(
                        code=code,
                        name=self.STOCKS_DB[code]["name"],
                        price=quote.price,
                        change_percent=quote.change_percent,
                    )
                )

        results.sort(key=lambda x: float(x.change_percent or 0))
        return results[:limit]

"""
同花顺数据源
"""

import httpx
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class TongHuaShunDataSource(BaseDataSource):
    """同花顺数据源"""

    def __init__(self):
        self.base_url = "https://stockapp10.10jqka.com.cn"
        self.timeout = httpx.Timeout(15.0, connect=10.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.10jqka.com.cn/",
        }

    def _convert_code(self, code: str) -> str:
        """转换股票代码格式"""
        if code.startswith("6"):
            return f"1.{code}"
        elif code.startswith(("0", "3")):
            return f"0.{code}"
        return code

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取单只股票行情"""
        try:
            url = f"{self.base_url}/quotation_api/stock/getindividuation"
            params = {"ids": code, "type": "rtq"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                if data.get("data") and code in data["data"]:
                    info = data["data"][code]
                    return StockQuoteResponse(
                        id=0,
                        stock_code=code,
                        price=Decimal(str(info.get("price", 0))),
                        open_price=Decimal(str(info.get("open", 0))),
                        high_price=Decimal(str(info.get("high", 0))),
                        low_price=Decimal(str(info.get("low", 0))),
                        pre_close=Decimal(str(info.get("pre_close", 0))),
                        change_percent=Decimal(str(info.get("change_pct", 0))),
                        volume=int(info.get("volume", 0)),
                        turnover=Decimal(str(info.get("amount", 0))),
                        timestamp=datetime.now(),
                    )
            return None
        except Exception as e:
            logger.error(f"同花顺获取行情失败 {code}: {e}")
            return None

    async def get_quotes(self, codes: List[str]) -> List[StockQuoteResponse]:
        """批量获取股票行情"""
        results = []
        for code in codes[:50]:
            quote = await self.get_quote(code)
            if quote:
                results.append(quote)
        return results

    async def get_kline(
        self, code: str, period: str = "day", limit: int = 200
    ) -> List[KlineData]:
        """获取K线数据"""
        try:
            period_map = {"day": "day", "week": "week", "month": "month"}

            url = f"{self.base_url}/quotation_api/stock/kline"
            params = {
                "fields": "f1,f2,f3,f4,f5,f6",
                "kline": period_map.get(period, "day"),
                "limit": str(min(limit, 500)),
                "stock": code,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                klines = []
                if data.get("data") and data["data"].get("klines"):
                    for line in data["data"]["klines"]:
                        parts = line.split(",")
                        klines.append(
                            KlineData(
                                time=int(
                                    datetime.strptime(parts[0], "%Y-%m-%d").timestamp()
                                ),
                                open=Decimal(parts[1]),
                                high=Decimal(parts[2]),
                                low=Decimal(parts[3]),
                                close=Decimal(parts[4]),
                                volume=int(parts[5]),
                            )
                        )
                return klines
        except Exception as e:
            logger.error(f"同花顺获取K线失败 {code}: {e}")
            return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票"""
        try:
            url = f"{self.base_url}/quotation_api/search"
            params = {"search": keyword, "market": "all"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                if data.get("data"):
                    for item in data["data"]:
                        code = item.get("code", "")
                        results.append(
                            StockSearchResult(
                                code=code,
                                name=item.get("name", ""),
                                market=item.get("market", ""),
                                industry=item.get("industry", ""),
                            )
                        )
                return results[:30]
        except Exception as e:
            logger.error(f"同花顺搜索失败: {e}")
            return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表"""
        try:
            url = f"{self.base_url}/quotation_api/hotstock"
            params = {"num": limit}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                if data.get("data"):
                    for item in data["data"]:
                        results.append(
                            StockSearchResult(
                                code=item.get("code", ""),
                                name=item.get("name", ""),
                                price=Decimal(str(item.get("price", 0)))
                                if item.get("price")
                                else None,
                                change_percent=Decimal(str(item.get("change_pct", 0)))
                                if item.get("change_pct")
                                else None,
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"同花顺获取列表失败: {e}")
            return []

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        """获取指数"""
        index_names = {"000001": "上证指数", "399001": "深证成指", "399006": "创业板指"}

        quote = await self.get_quote(code)
        if quote:
            return StockSearchResult(
                code=code,
                name=index_names.get(code, code),
                price=quote.price,
                change_percent=quote.change_percent,
            )
        return None

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取涨幅榜"""
        try:
            url = f"{self.base_url}/quotation_api/hotstock"
            params = {"num": limit, "order": "change_pct", "sort": "desc"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                if data.get("data"):
                    for item in data["data"]:
                        results.append(
                            StockSearchResult(
                                code=item.get("code", ""),
                                name=item.get("name", ""),
                                price=Decimal(str(item.get("price", 0)))
                                if item.get("price")
                                else None,
                                change_percent=Decimal(str(item.get("change_pct", 0)))
                                if item.get("change_pct")
                                else None,
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"同花顺获取涨幅榜失败: {e}")
            return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取跌幅榜"""
        try:
            url = f"{self.base_url}/quotation_api/hotstock"
            params = {"num": limit, "order": "change_pct", "sort": "asc"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                if data.get("data"):
                    for item in data["data"]:
                        results.append(
                            StockSearchResult(
                                code=item.get("code", ""),
                                name=item.get("name", ""),
                                price=Decimal(str(item.get("price", 0)))
                                if item.get("price")
                                else None,
                                change_percent=Decimal(str(item.get("change_pct", 0)))
                                if item.get("change_pct")
                                else None,
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"同花顺获取跌幅榜失败: {e}")
            return []

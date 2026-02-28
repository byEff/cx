"""
东方财富数据源
"""

import httpx
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class EastMoneyDataSource(BaseDataSource):
    """东方财富数据源"""

    def __init__(self):
        self.base_url = "https://push2.eastmoney.com/api/qt"
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def _get_secid(self, code: str) -> str:
        """获取东方财富secid"""
        if code.startswith(("6", "9")):
            return f"1.{code}"  # 上海
        else:
            return f"0.{code}"  # 深圳

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取单只股票行情"""
        try:
            secid = self._get_secid(code)
            url = f"{self.base_url}/stock/get"
            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f58,f60,f170,f171",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                if data.get("data"):
                    d = data["data"]
                    return StockQuoteResponse(
                        id=0,
                        stock_code=code,
                        price=Decimal(str(d.get("f43", 0) / 100)),
                        open_price=Decimal(str(d.get("f46", 0) / 100)),
                        high_price=Decimal(str(d.get("f44", 0) / 100)),
                        low_price=Decimal(str(d.get("f45", 0) / 100)),
                        pre_close=Decimal(str(d.get("f60", 0) / 100)),
                        change_percent=Decimal(str(d.get("f170", 0) / 100)),
                        volume=int(d.get("f47", 0)),
                        turnover=Decimal(str(d.get("f48", 0))),
                        timestamp=datetime.now(),
                    )
            return None
        except Exception as e:
            logger.error(f"东方财富获取行情失败 {code}: {e}")
            return None

    async def get_quotes(self, codes: List[str]) -> List[StockQuoteResponse]:
        """批量获取股票行情"""
        results = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
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
            secid = self._get_secid(code)
            klt_map = {"day": "101", "week": "102", "month": "103"}

            url = f"{self.base_url}/stock/kline/get"
            params = {
                "secid": secid,
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57",
                "klt": klt_map.get(period, "101"),
                "fqt": "1",
                "end": "20500101",
                "lmt": str(min(limit, 500)),
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
            logger.error(f"东方财富获取K线失败 {code}: {e}")
            return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票"""
        try:
            url = f"{self.base_url}/stock/list"
            params = {
                "pn": 1,
                "pz": 100,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f4,f5,f6,f7,f12,f14,f100",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                keyword_lower = keyword.lower()
                if data.get("data") and data["data"].get("diff"):
                    for item in data["data"]["diff"]:
                        code = item.get("f12", "")
                        name = item.get("f14", "")
                        if (
                            keyword_lower in code.lower()
                            or keyword_lower in name.lower()
                        ):
                            market = "SZ" if code.startswith(("0", "3")) else "SH"
                            results.append(
                                StockSearchResult(
                                    code=code,
                                    name=name,
                                    price=Decimal(str(item.get("f2", 0) / 100))
                                    if item.get("f2")
                                    else None,
                                    change_percent=Decimal(str(item.get("f3", 0) / 100))
                                    if item.get("f3")
                                    else None,
                                    market=market,
                                    industry=item.get("f100", ""),
                                )
                            )
                return results[:30]
        except Exception as e:
            logger.error(f"东方财富搜索失败: {e}")
            return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表"""
        try:
            url = f"{self.base_url}/stock/list"
            params = {
                "pn": 1,
                "pz": limit,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f4,f5,f6,f7,f12,f14,f100",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                if data.get("data") and data["data"].get("diff"):
                    for item in data["data"]["diff"]:
                        code = item.get("f12", "")
                        results.append(
                            StockSearchResult(
                                code=code,
                                name=item.get("f14", ""),
                                price=Decimal(str(item.get("f2", 0) / 100))
                                if item.get("f2")
                                else None,
                                change_percent=Decimal(str(item.get("f3", 0) / 100))
                                if item.get("f3")
                                else None,
                                market="SZ" if code.startswith(("0", "3")) else "SH",
                                industry=item.get("f100", ""),
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"东方财富获取列表失败: {e}")
            return []

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        """获取指数"""
        index_names = {
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
            "000300": "沪深300",
            "000905": "中证500",
        }

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
        return await self._get_top_stocks("f3", "desc", limit)

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取跌幅榜"""
        return await self._get_top_stocks("f3", "asc", limit)

    async def _get_top_stocks(
        self, sort_field: str, sort_order: str, limit: int
    ) -> List[StockSearchResult]:
        """获取排名靠前的股票"""
        try:
            url = f"{self.base_url}/stock/list"
            params = {
                "pn": 1,
                "pz": limit,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f4,f5,f6,f7,f12,f14",
                "s": f"{sort_field} {sort_order}",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                if data.get("data") and data["data"].get("diff"):
                    for item in data["data"]["diff"]:
                        results.append(
                            StockSearchResult(
                                code=item.get("f12", ""),
                                name=item.get("f14", ""),
                                price=Decimal(str(item.get("f2", 0) / 100))
                                if item.get("f2")
                                else None,
                                change_percent=Decimal(str(item.get("f3", 0) / 100))
                                if item.get("f3")
                                else None,
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"东方财富获取排行榜失败: {e}")
            return []

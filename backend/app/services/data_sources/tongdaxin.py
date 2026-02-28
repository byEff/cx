"""
通达信数据源
"""

import httpx
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import struct
import base64
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class TongDaXinDataSource(BaseDataSource):
    """通达信数据源"""

    def __init__(self):
        self.base_url = "http://push2.eastmoney.com"
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
        }

    def _get_secid(self, code: str) -> str:
        """获取通达信secid"""
        if code.startswith(("6", "9")):
            return f"1.{code}"
        else:
            return f"0.{code}"

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取单只股票行情"""
        try:
            secid = self._get_secid(code)
            url = f"{self.base_url}/api/qt/stock/get"
            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f58,f60,f170,f171,f173",
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
            logger.error(f"通达信获取行情失败 {code}: {e}")
            return None

    async def get_quotes(self, codes: List[str]) -> List[StockQuoteResponse]:
        """批量获取股票行情"""
        try:
            secids = ",".join([self._get_secid(c) for c in codes])
            url = f"{self.base_url}/api/qt/ulist.np/get"
            params = {
                "fltt": 2,
                "invt": 2,
                "fields": "f1,f2,f3,f4,f5,f6,f7,f12,f13,f14,f100,f104,f105,f106",
                "secids": secids,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                results = []
                if data.get("data") and data["data"].get("diff"):
                    for item in data["data"]["diff"]:
                        code = item.get("f12", "")
                        results.append(
                            StockQuoteResponse(
                                id=0,
                                stock_code=code,
                                price=Decimal(str(item.get("f2", 0)))
                                if item.get("f2", 0) != "-"
                                else Decimal("0"),
                                open_price=Decimal(str(item.get("f17", 0)))
                                if item.get("f17", 0) != "-"
                                else Decimal("0"),
                                high_price=Decimal(str(item.get("f15", 0)))
                                if item.get("f15", 0) != "-"
                                else Decimal("0"),
                                low_price=Decimal(str(item.get("f16", 0)))
                                if item.get("f16", 0) != "-"
                                else Decimal("0"),
                                pre_close=Decimal(str(item.get("f18", 0)))
                                if item.get("f18", 0) != "-"
                                else Decimal("0"),
                                change_percent=Decimal(str(item.get("f4", 0)))
                                if item.get("f4", 0) != "-"
                                else Decimal("0"),
                                volume=int(item.get("f5", 0)) if item.get("f5") else 0,
                                turnover=Decimal(str(item.get("f6", 0)))
                                if item.get("f6", 0) != "-"
                                else Decimal("0"),
                                timestamp=datetime.now(),
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"通达信批量获取行情失败: {e}")
            # 降级为单条获取
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
            secid = self._get_secid(code)
            klt_map = {
                "day": "101",
                "week": "102",
                "month": "103",
                "1min": "1",
                "5min": "5",
                "15min": "15",
                "30min": "30",
                "60min": "60",
            }

            url = f"{self.base_url}/api/qt/stock/kline/get"
            params = {
                "secid": secid,
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                "klt": klt_map.get(period, "101"),
                "fqt": "1",
                "end": "20500101",
                "lmt": str(min(limit, 1000)),
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
                                    datetime.strptime(
                                        parts[0], "%Y-%m-%d %H:%M:%S"
                                    ).timestamp()
                                )
                                if len(parts) > 6 and ":" in parts[0]
                                else int(
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
            logger.error(f"通达信获取K线失败 {code}: {e}")
            return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票"""
        try:
            url = f"{self.base_url}/api/qt/ulist.np/get"
            params = {
                "fltt": 2,
                "invt": 2,
                "fields": "f12,f13,f14,f100",
                "pn": 1,
                "pz": 50,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fid": "f3",
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
                                    market=market,
                                    industry=item.get("f100", ""),
                                )
                            )
                return results[:30]
        except Exception as e:
            logger.error(f"通达信搜索失败: {e}")
            return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表"""
        try:
            url = f"{self.base_url}/api/qt/ulist.np/get"
            params = {
                "fltt": 2,
                "invt": 2,
                "fields": "f2,f3,f4,f12,f14,f100",
                "pn": 1,
                "pz": limit,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
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
                                price=Decimal(str(item.get("f2", 0)))
                                if item.get("f2", 0) != "-"
                                else None,
                                change_percent=Decimal(str(item.get("f3", 0)))
                                if item.get("f3", 0) != "-"
                                else None,
                                industry=item.get("f100", ""),
                                market="SZ"
                                if item.get("f12", "").startswith(("0", "3"))
                                else "SH",
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"通达信获取列表失败: {e}")
            return []

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        """获取指数"""
        index_names = {
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
            "000300": "沪深300",
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
            url = f"{self.base_url}/api/qt/ulist.np/get"
            params = {
                "fltt": 2,
                "invt": 2,
                "fields": "f2,f3,f4,f12,f14",
                "pn": 1,
                "pz": limit,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fid": sort_field,
                "sort": "asc" if sort_order == "asc" else "desc",
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
                                price=Decimal(str(item.get("f2", 0)))
                                if item.get("f2", 0) != "-"
                                else None,
                                change_percent=Decimal(str(item.get("f3", 0)))
                                if item.get("f3", 0) != "-"
                                else None,
                            )
                        )
                return results
        except Exception as e:
            logger.error(f"通达信获取排行榜失败: {e}")
            return []

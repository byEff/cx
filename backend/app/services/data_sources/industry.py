"""
行业板块数据源 - 使用东方财富API获取板块指数数据
"""

import httpx
from typing import List, Optional, Dict, Any
from loguru import logger
from decimal import Decimal

from .base import BaseDataSource


class IndustryDataSource(BaseDataSource):
    """行业板块数据源 - 使用东方财富API"""

    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://quote.eastmoney.com/",
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout, headers=self.headers)
        return self._client

    async def get_industry_list(self, limit: int = 500) -> List[dict]:
        """获取行业板块列表"""
        try:
            url = "https://push2delay.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 2000,
                "fs": "b:MK0878",
                "fields": "f12,f14,f2,f3,f5,f6,f100",
            }

            client = await self._get_client()
            response = await client.get(url, params=params)
            data = response.json()

            industries = []
            if data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue

                    code = item.get("f12", "")
                    name = item.get("f14", "")

                    if not code or not name:
                        continue

                    price = item.get("f2", 0)
                    change_percent = item.get("f3", 0)
                    volume = item.get("f5", 0)
                    turnover = item.get("f6", 0)

                    industries.append(
                        {
                            "code": code,
                            "name": name,
                            "price": Decimal(str(price / 100)) if price else None,
                            "change_percent": Decimal(str(change_percent / 100))
                            if change_percent
                            else None,
                            "volume": volume,
                            "turnover": Decimal(str(turnover)) if turnover else None,
                            "change_5d": None,
                            "change_1m": None,
                            "change_ytd": None,
                            "stock_count": item.get("f100"),
                            "lead_stock": "",
                        }
                    )

            logger.info(f"成功获取 {len(industries)} 个行业板块")
            return industries[:limit]

        except Exception as e:
            logger.error(f"获取行业列表失败：{e}")
            return await self._get_fallback_industries()

    async def get_board_stocks(self, board_code: str, limit: int = 100) -> List[dict]:
        """获取板块内股票列表"""
        try:
            url = "https://push2delay.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": limit,
                "fs": f"b:{board_code}",
                "fields": "f12,f14,f2,f3,f5,f6",
            }

            client = await self._get_client()
            response = await client.get(url, params=params)
            data = response.json()

            stocks = []
            if data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue

                    code = item.get("f12", "")
                    name = item.get("f14", "")

                    if not code or not name:
                        continue

                    price = item.get("f2", 0)
                    change_percent = item.get("f3", 0)

                    stocks.append(
                        {
                            "code": code,
                            "name": name,
                            "price": Decimal(str(price / 100)) if price else None,
                            "change_percent": Decimal(str(change_percent / 100))
                            if change_percent
                            else None,
                            "volume": item.get("f5"),
                            "turnover": item.get("f6"),
                            "market": "SH" if code.startswith("6") else "SZ",
                        }
                    )

            return stocks

        except Exception as e:
            logger.error(f"获取板块股票失败 {board_code}: {e}")
            return []

    async def _get_fallback_industries(self) -> List[dict]:
        """备用数据"""
        return []

    async def get_industry_detail(self, code: str) -> Optional[dict]:
        """获取行业详情"""
        industries = await self.get_industry_list(500)
        for ind in industries:
            if ind.get("code") == code:
                return ind
        return None

    async def get_quote(self, code: str):
        return None

    async def get_quotes(self, codes: list):
        return []

    async def get_kline(self, code: str, period: str = "day", limit: int = 200):
        return []

    async def search(self, keyword: str):
        return []

    async def get_stock_list(self, industry: Optional[str] = None, limit: int = 50):
        return []

    async def get_index(self, code: str):
        return None

    async def get_top_gainers(self, limit: int = 10):
        return []

    async def get_top_losers(self, limit: int = 10):
        return []

    async def close(self):
        """关闭客户端连接"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

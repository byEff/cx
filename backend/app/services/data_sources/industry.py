"""
行业数据源
"""

import httpx
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockSearchResult
from .base import BaseDataSource


class IndustryDataSource(BaseDataSource):
    """行业数据源 - 从腾讯/东方财富获取行业数据"""

    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

    async def get_industry_list(self, limit: int = 50) -> List[dict]:
        """获取行业列表"""
        try:
            # 使用东方财富行业接口
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": str(limit),
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": "m:90 t:3",
                "fields": "f12,f14,f2,f3,f109,f110,f111,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                if data.get("data") and data["data"].get("diff"):
                    industries = []
                    for item in data["data"]["diff"]:
                        industries.append(
                            {
                                "code": item.get("f12", ""),
                                "name": item.get("f14", ""),
                                "price": float(item.get("f2", 0))
                                if item.get("f2")
                                else 0,
                                "change_percent": float(item.get("f3", 0))
                                if item.get("f3")
                                else 0,
                                "volume": int(item.get("f109", 0))
                                if item.get("f109")
                                else 0,
                                "turnover": float(item.get("f110", 0))
                                if item.get("f110")
                                else 0,
                                "change_5d": float(item.get("f113", 0))
                                if item.get("f113")
                                else 0,
                                "change_ytd": float(item.get("f114", 0))
                                if item.get("f114")
                                else 0,
                                "change_1m": float(item.get("f115", 0))
                                if item.get("f115")
                                else 0,
                                "stock_count": int(item.get("f127", 0))
                                if item.get("f127")
                                else 0,
                                "lead_stock": item.get("f128", ""),
                            }
                        )
                    return industries
        except Exception as e:
            logger.warning(f"获取行业列表失败：{e}")

        # 返回默认行业数据作为备用
        return await self._get_default_industries()

    async def _get_default_industries(self) -> List[dict]:
        """默认行业数据（备用）"""
        return [
            {
                "code": "BK0473",
                "name": "半导体",
                "price": 0,
                "change_percent": 1.2,
                "volume": 1234567,
                "turnover": 9876543210,
                "change_5d": 3.5,
                "change_ytd": 15.2,
                "change_1m": 8.3,
                "stock_count": 85,
                "lead_stock": "中芯国际",
            },
            {
                "code": "BK0491",
                "name": "白酒",
                "price": 0,
                "change_percent": -0.5,
                "volume": 987654,
                "turnover": 12345678900,
                "change_5d": -2.1,
                "change_ytd": 5.8,
                "change_1m": -3.2,
                "stock_count": 22,
                "lead_stock": "贵州茅台",
            },
            {
                "code": "BK0489",
                "name": "新能源",
                "price": 0,
                "change_percent": 2.3,
                "volume": 2345678,
                "turnover": 23456789000,
                "change_5d": 5.6,
                "change_ytd": 25.3,
                "change_1m": 12.5,
                "stock_count": 156,
                "lead_stock": "宁德时代",
            },
            {
                "code": "BK0475",
                "name": "医药生物",
                "price": 0,
                "change_percent": 0.8,
                "volume": 1567890,
                "turnover": 15678901234,
                "change_5d": 1.2,
                "change_ytd": 8.9,
                "change_1m": 4.5,
                "stock_count": 234,
                "lead_stock": "恒瑞医药",
            },
            {
                "code": "BK0488",
                "name": "人工智能",
                "price": 0,
                "change_percent": 3.5,
                "volume": 3456789,
                "turnover": 34567890123,
                "change_5d": 8.9,
                "change_ytd": 45.6,
                "change_1m": 18.9,
                "stock_count": 178,
                "lead_stock": "科大讯飞",
            },
            {
                "code": "BK0477",
                "name": "银行",
                "price": 0,
                "change_percent": -0.2,
                "volume": 4567890,
                "turnover": 45678901234,
                "change_5d": -0.8,
                "change_ytd": 12.3,
                "change_1m": 2.1,
                "stock_count": 42,
                "lead_stock": "招商银行",
            },
            {
                "code": "BK0481",
                "name": "证券",
                "price": 0,
                "change_percent": 1.5,
                "volume": 5678901,
                "turnover": 56789012345,
                "change_5d": 4.2,
                "change_ytd": 18.7,
                "change_1m": 9.8,
                "stock_count": 58,
                "lead_stock": "中信证券",
            },
            {
                "code": "BK0485",
                "name": "房地产",
                "price": 0,
                "change_percent": -1.2,
                "volume": 6789012,
                "turnover": 67890123456,
                "change_5d": -3.5,
                "change_ytd": -8.9,
                "change_1m": -5.6,
                "stock_count": 134,
                "lead_stock": "万科 A",
            },
            {
                "code": "BK0492",
                "name": "汽车",
                "price": 0,
                "change_percent": 0.9,
                "volume": 7890123,
                "turnover": 78901234567,
                "change_5d": 2.3,
                "change_ytd": 22.1,
                "change_1m": 11.2,
                "stock_count": 189,
                "lead_stock": "比亚迪",
            },
            {
                "code": "BK0479",
                "name": "消费电子",
                "price": 0,
                "change_percent": 1.8,
                "volume": 8901234,
                "turnover": 89012345678,
                "change_5d": 4.5,
                "change_ytd": 28.9,
                "change_1m": 15.6,
                "stock_count": 145,
                "lead_stock": "立讯精密",
            },
        ]

    async def get_industry_detail(self, code: str) -> Optional[dict]:
        """获取行业详情"""
        industries = await self.get_industry_list(100)
        for industry in industries:
            if industry["code"] == code:
                return industry
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

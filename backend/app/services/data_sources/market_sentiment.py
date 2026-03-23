"""
市场情绪数据源 - 涨跌分布、涨停统计、热门股、成交量分布
"""

import httpx
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockSearchResult


class MarketSentimentDataSource:
    """市场情绪数据源 - 使用同花顺数据"""

    def __init__(self):
        self.base_url = "https://dq.10jqka.com.cn"
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://stockpage.10jqka.com.cn/",
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout, headers=self.headers)
        return self._client

    async def get_up_down_distribution(self) -> Dict[str, Any]:
        """获取涨跌家数分布"""
        try:
            url = f"{self.base_url}/fuyao/up_down_distribution/distribution/v2/realtime"
            client = await self._get_client()
            response = await client.get(url)
            data = response.json()

            if data.get("status_code") == 0 and data.get("data"):
                d = data["data"]
                return {
                    "up_count": d.get("up", 0),
                    "down_count": d.get("down", 0),
                    "flat_count": d.get("flat", 0),
                    "limit_up": d.get("limit_up", 0),
                    "limit_down": d.get("limit_down", 0),
                    "up_limit_count": d.get("limit_up", 0),
                    "down_limit_count": d.get("limit_down", 0),
                    "timestamp": datetime.now().isoformat(),
                }

            return await self._get_up_down_from_eastmoney()

        except Exception as e:
            logger.error(f"获取涨跌分布失败: {e}")
            return await self._get_up_down_from_eastmoney()

    async def _get_up_down_from_eastmoney(self) -> Dict[str, Any]:
        """从东方财富获取涨跌分布（备用）"""
        try:
            url = "https://push2delay.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 5000,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f3",
            }

            client = await self._get_client()
            response = await client.get(url, params=params)
            data = response.json()

            up_count = 0
            down_count = 0
            flat_count = 0
            limit_up = 0
            limit_down = 0

            if data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue
                    change = item.get("f3", 0)
                    if change is None:
                        continue
                    change_value = change / 100

                    if change_value > 0:
                        up_count += 1
                        if change_value >= 9.9:
                            limit_up += 1
                    elif change_value < 0:
                        down_count += 1
                        if change_value <= -9.9:
                            limit_down += 1
                    else:
                        flat_count += 1

            return {
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": flat_count,
                "limit_up": limit_up,
                "limit_down": limit_down,
                "up_limit_count": limit_up,
                "down_limit_count": limit_down,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"从东方财富获取涨跌分布失败: {e}")
            return {
                "up_count": 0,
                "down_count": 0,
                "flat_count": 0,
                "limit_up": 0,
                "limit_down": 0,
                "up_limit_count": 0,
                "down_limit_count": 0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def get_limit_up_stats(self) -> Dict[str, Any]:
        """获取涨停板统计"""
        try:
            return await self._get_limit_up_stats_from_eastmoney()
        except Exception as e:
            logger.error(f"获取涨停统计失败: {e}")
            return {
                "total_count": 0,
                "seal_count": 0,
                "open_count": 0,
                "time_distribution": {},
                "board_distribution": {},
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def _get_limit_up_stats_from_eastmoney(self) -> Dict[str, Any]:
        """从东方财富获取涨停统计"""
        try:
            url = "https://push2delay.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 500,
                "fs": "b:MK0878",
                "fields": "f12,f14,f2,f3",
            }

            client = await self._get_client()
            response = await client.get(url, params=params)
            data = response.json()

            total_count = 0
            if data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    total_count = len(diff_data)
                else:
                    total_count = len(diff_data)

            return {
                "total_count": total_count,
                "seal_count": total_count,
                "open_count": 0,
                "time_distribution": {},
                "board_distribution": {},
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"从东方财富获取涨停统计失败: {e}")
            return {
                "total_count": 0,
                "seal_count": 0,
                "open_count": 0,
                "time_distribution": {},
                "board_distribution": {},
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def get_hot_stocks(self, limit: int = 20) -> List[StockSearchResult]:
        """获取热门股票榜单（按成交量排序）"""
        try:
            url = "https://push2delay.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": limit * 3,  # 获取更多数据用于排序
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f12,f14,f2,f3,f5,f6",
            }

            client = await self._get_client()
            response = await client.get(url, params=params)
            data = response.json()

            results = []
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
                    market = "SH" if code.startswith("6") else "SZ"
                    volume = item.get("f5", 0)

                    if volume > 0:  # 只包含有成交量的股票
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
                                volume=volume,
                                market=market,
                            )
                        )

            # 按成交量降序排序
            results.sort(key=lambda x: x.volume or 0, reverse=True)

            return results[:limit]
        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return []

    async def close(self):
        """关闭客户端连接"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


_market_sentiment_source: Optional[MarketSentimentDataSource] = None


def get_market_sentiment_source() -> MarketSentimentDataSource:
    """获取市场情绪数据源单例"""
    global _market_sentiment_source
    if _market_sentiment_source is None:
        _market_sentiment_source = MarketSentimentDataSource()
    return _market_sentiment_source

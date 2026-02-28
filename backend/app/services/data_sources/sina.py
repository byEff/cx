"""
新浪财经数据源 - 备用数据源
"""

import httpx
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class SinaDataSource(BaseDataSource):
    """新浪财经数据源"""

    def __init__(self):
        self.base_url = "https://hq.sinajs.cn"
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://finance.sina.com.cn",
        }

    def _get_code(self, code: str) -> str:
        """转换股票代码为新浪格式"""
        if code.startswith("6"):
            return f"sh{code}"
        else:
            return f"sz{code}"

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取单只股票行情"""
        try:
            sina_code = self._get_code(code)
            url = f"{self.base_url}/list={sina_code}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                text = response.text

                # 解析新浪返回的数据
                # var hq_str_sh600000="浦发银行,15.80,16.10,..."
                if "hq_str" in text:
                    start = text.find('"') + 1
                    end = text.find('"', start)
                    data = text[start:end].split(",")

                    if len(data) >= 33:
                        return StockQuoteResponse(
                            id=0,
                            stock_code=code,
                            price=Decimal(data[1]) if data[1] else Decimal("0"),
                            open_price=Decimal(data[5]) if data[5] else Decimal("0"),
                            high_price=Decimal(data[4]) if data[4] else Decimal("0"),
                            low_price=Decimal(data[5]) if data[5] else Decimal("0"),
                            pre_close=Decimal(data[2]) if data[2] else Decimal("0"),
                            change_percent=Decimal(
                                str(
                                    (float(data[1]) - float(data[2]))
                                    / float(data[2])
                                    * 100
                                )
                            )
                            if data[2] and float(data[2]) != 0
                            else Decimal("0"),
                            volume=int(float(data[8]) * 100) if data[8] else 0,
                            turnover=Decimal(data[9]) if data[9] else Decimal("0"),
                            timestamp=datetime.now(),
                        )
            return None
        except Exception as e:
            logger.error(f"新浪获取行情失败 {code}: {e}")
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
        """获取K线数据 - 新浪不支持K线"""
        return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票 - 使用简单的股票列表"""
        try:
            # 常用股票列表
            common_stocks = [
                {"code": "000001", "name": "平安银行"},
                {"code": "000002", "name": "万科A"},
                {"code": "000651", "name": "格力电器"},
                {"code": "000858", "name": "五粮液"},
                {"code": "600000", "name": "浦发银行"},
                {"code": "600036", "name": "招商银行"},
                {"code": "600519", "name": "贵州茅台"},
                {"code": "601318", "name": "中国平安"},
                {"code": "601888", "name": "中国中免"},
                {"code": "603259", "name": "药明康德"},
            ]

            keyword_lower = keyword.lower()
            results = []
            for stock in common_stocks:
                if (
                    keyword_lower in stock["code"].lower()
                    or keyword_lower in stock["name"].lower()
                ):
                    results.append(
                        StockSearchResult(
                            code=stock["code"],
                            name=stock["name"],
                            market="SZ"
                            if stock["code"].startswith(("0", "3"))
                            else "SH",
                        )
                    )

            return results
        except Exception as e:
            logger.error(f"新浪搜索失败: {e}")
            return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表"""
        return await self.search("")

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
        return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取跌幅榜"""
        return []

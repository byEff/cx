"""
AkShare数据源
参考: https://akshare.akfamily.xyz/
"""

import akshare as ak
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class AkShareDataSource(BaseDataSource):
    """AkShare数据源"""

    def __init__(self):
        self.is_available = True
        logger.info("AkShare数据源初始化成功")

    def _get_market_suffix(self, code: str) -> str:
        if code.startswith(("6", "9")):
            return "sh"
        return "sz"

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        try:
            market = self._get_market_suffix(code)
            df = ak.stock_zh_a_spot_em()

            stock = df[df["代码"] == code]
            if stock.empty:
                return None

            row = stock.iloc[0]
            price = float(row.get("最新价", 0) or 0)
            pre_close = float(row.get("昨收", 0) or price)
            change_percent = float(row.get("涨跌幅", 0) or 0)

            return StockQuoteResponse(
                id=0,
                stock_code=code,
                price=Decimal(str(price)),
                open_price=Decimal(str(row.get("今开", price))),
                high_price=Decimal(str(row.get("最高", price))),
                low_price=Decimal(str(row.get("最低", price))),
                pre_close=Decimal(str(pre_close)),
                change_percent=Decimal(str(round(change_percent, 2))),
                volume=int(row.get("成交量", 0) or 0),
                turnover=Decimal(str(row.get("成交额", 0) or 0)),
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.warning(f"AkShare获取行情失败 {code}: {e}")
        return None

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
        try:
            market = self._get_market_suffix(code)
            symbol = f"{market}{code}"

            if period == "day":
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            elif period == "week":
                df = ak.stock_zh_a_hist(symbol=symbol, period="weekly", adjust="qfq")
            elif period == "month":
                df = ak.stock_zh_a_hist(symbol=symbol, period="monthly", adjust="qfq")
            else:
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")

            if df.empty:
                return []

            klines = []
            df = df.tail(limit)

            for _, row in df.iterrows():
                try:
                    date_str = str(row.get("日期", ""))
                    dt = datetime.strptime(date_str, "%Y-%m-%d")

                    klines.append(
                        KlineData(
                            time=int(dt.timestamp()),
                            open=Decimal(str(row.get("开盘", 0))),
                            high=Decimal(str(row.get("最高", 0))),
                            low=Decimal(str(row.get("最低", 0))),
                            close=Decimal(str(row.get("收盘", 0))),
                            volume=int(row.get("成交量", 0)),
                        )
                    )
                except Exception as e:
                    logger.warning(f"解析K线数据失败: {e}")

            return klines
        except Exception as e:
            logger.warning(f"AkShare获取K线失败 {code}: {e}")
        return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        try:
            df = ak.stock_zh_a_spot_em()
            keyword_upper = keyword.upper()

            results = []
            for _, row in df.iterrows():
                code = str(row.get("代码", ""))
                name = str(row.get("名称", ""))

                if keyword_upper in code or keyword in name:
                    price = row.get("最新价")
                    change = row.get("涨跌幅")

                    results.append(
                        StockSearchResult(
                            code=code,
                            name=name,
                            price=Decimal(str(price)) if price else None,
                            change_percent=Decimal(str(change)) if change else None,
                            market="SH" if code.startswith(("6", "9")) else "SZ",
                        )
                    )

                    if len(results) >= 20:
                        break

            return results
        except Exception as e:
            logger.warning(f"AkShare搜索失败: {e}")
        return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        try:
            df = ak.stock_zh_a_spot_em()

            results = []
            for _, row in df.head(limit).iterrows():
                code = str(row.get("代码", ""))
                name = str(row.get("名称", ""))
                price = row.get("最新价")
                change = row.get("涨跌幅")

                results.append(
                    StockSearchResult(
                        code=code,
                        name=name,
                        price=Decimal(str(price)) if price else None,
                        change_percent=Decimal(str(change)) if change else None,
                        market="SH" if code.startswith(("6", "9")) else "SZ",
                    )
                )

            return results
        except Exception as e:
            logger.warning(f"AkShare获取股票列表失败: {e}")
        return []

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        return None

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        try:
            df = ak.stock_zh_a_spot_em()
            df = df.sort_values("涨跌幅", ascending=False).head(limit)

            results = []
            for _, row in df.iterrows():
                code = str(row.get("代码", ""))
                name = str(row.get("名称", ""))
                price = row.get("最新价")
                change = row.get("涨跌幅")

                results.append(
                    StockSearchResult(
                        code=code,
                        name=name,
                        price=Decimal(str(price)) if price else None,
                        change_percent=Decimal(str(change)) if change else None,
                        market="SH" if code.startswith(("6", "9")) else "SZ",
                    )
                )

            return results
        except Exception as e:
            logger.warning(f"AkShare获取涨幅榜失败: {e}")
        return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        try:
            df = ak.stock_zh_a_spot_em()
            df = df.sort_values("涨跌幅", ascending=True).head(limit)

            results = []
            for _, row in df.iterrows():
                code = str(row.get("代码", ""))
                name = str(row.get("名称", ""))
                price = row.get("最新价")
                change = row.get("涨跌幅")

                results.append(
                    StockSearchResult(
                        code=code,
                        name=name,
                        price=Decimal(str(price)) if price else None,
                        change_percent=Decimal(str(change)) if change else None,
                        market="SH" if code.startswith(("6", "9")) else "SZ",
                    )
                )

            return results
        except Exception as e:
            logger.warning(f"AkShare获取跌幅榜失败: {e}")
        return []

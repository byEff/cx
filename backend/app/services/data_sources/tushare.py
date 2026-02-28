"""
Tushare数据源
需要配置token，参考: https://tushare.pro/
"""

import os
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class TushareDataSource(BaseDataSource):
    """Tushare数据源"""

    def __init__(self):
        self.token = os.getenv("TUSHARE_TOKEN", "")
        self.pro = None
        if self.token:
            try:
                import tushare as ts

                ts.set_token(self.token)
                self.pro = ts.pro_api()
                logger.info("Tushare数据源初始化成功")
            except Exception as e:
                logger.warning(f"Tushare初始化失败: {e}")
        self.is_available = self.pro is not None

    def _get_market(self, code: str) -> str:
        if code.startswith(("6", "9")):
            return "SH"
        return "SZ"

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        if not self.pro:
            return None

        try:
            df = self.pro.daily(
                ts_code=f"{code}.{'SH' if code.startswith(('6', '9')) else 'SZ'}"
            )
            if df.empty:
                return None

            latest = df.iloc[0]
            pre_close = float(latest.get("pre_close", 0))
            close = float(latest.get("close", 0))
            change_percent = ((close - pre_close) / pre_close * 100) if pre_close else 0

            return StockQuoteResponse(
                id=0,
                stock_code=code,
                price=Decimal(str(close)),
                open_price=Decimal(str(latest.get("open", 0))),
                high_price=Decimal(str(latest.get("high", 0))),
                low_price=Decimal(str(latest.get("low", 0))),
                pre_close=Decimal(str(pre_close)),
                change_percent=Decimal(str(round(change_percent, 2))),
                volume=int(latest.get("vol", 0)),
                turnover=Decimal(str(latest.get("amount", 0))),
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.warning(f"Tushare获取行情失败 {code}: {e}")
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
        if not self.pro:
            return []

        try:
            ts_code = f"{code}.{'SH' if code.startswith(('6', '9')) else 'SZ'}"

            freq_map = {"day": "D", "week": "W", "month": "M"}
            freq = freq_map.get(period, "D")

            df = self.pro.daily(ts_code=ts_code, limit=limit)
            if df.empty:
                return []

            klines = []
            for _, row in df.iterrows():
                trade_date = row.get("trade_date", "")
                try:
                    dt = datetime.strptime(str(trade_date), "%Y%m%d")
                    klines.append(
                        KlineData(
                            time=int(dt.timestamp()),
                            open=Decimal(str(row.get("open", 0))),
                            high=Decimal(str(row.get("high", 0))),
                            low=Decimal(str(row.get("low", 0))),
                            close=Decimal(str(row.get("close", 0))),
                            volume=int(row.get("vol", 0)),
                        )
                    )
                except:
                    pass

            return list(reversed(klines))
        except Exception as e:
            logger.warning(f"Tushare获取K线失败 {code}: {e}")
        return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        if not self.pro:
            return []

        try:
            df = self.pro.stock_basic(
                exchange="", list_status="L", fields="ts_code,symbol,name,market"
            )
            if df.empty:
                return []

            results = []
            for _, row in df.head(limit).iterrows():
                code = str(row.get("symbol", ""))
                name = str(row.get("name", ""))
                if keyword.upper() in code or keyword in name:
                    market = "SH" if code.startswith(("6", "9")) else "SZ"
                    results.append(
                        StockSearchResult(code=code, name=name, market=market)
                    )
            return results
        except Exception as e:
            logger.warning(f"Tushare获取股票列表失败: {e}")
        return []

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        return None

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        return []

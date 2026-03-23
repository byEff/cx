"""
东方财富数据源 - 增强版
支持多域名容错、新搜索接口、完整字段映射
"""

import httpx
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class EastMoneyDataSource(BaseDataSource):
    """东方财富数据源 - 增强版"""

    DOMAINS = {
        "push2his": [
            "https://push2his.eastmoney.com",
            "https://push2his.deno.dev",
        ],
        "push2delay": [
            "https://push2delay.eastmoney.com",
            "https://push2delay.deno.dev",
        ],
        "searchapi": [
            "https://searchapi.eastmoney.com",
            "https://searchapi.deno.dev",
        ],
        "push2": [
            "https://push2.eastmoney.com",
        ],
        "datacenter": [
            "https://datacenter.eastmoney.com",
        ],
    }

    FIELDS_BASIC = "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26"

    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout, headers=self.headers)
        return self._client

    async def _request_with_fallback(
        self,
        domain_key: str,
        endpoint: str,
        params: Dict[str, Any],
        timeout: float = 10.0,
    ) -> Optional[Dict]:
        """带容错的请求方法"""
        domains = self.DOMAINS.get(domain_key, [])
        client = await self._get_client()

        for i, domain in enumerate(domains):
            try:
                url = f"{domain}{endpoint}"
                response = await client.get(url, params=params, timeout=timeout)
                data = response.json()
                if data:
                    return data
            except Exception as e:
                if i == 0:
                    logger.warning(f"[{domain_key}] 主域名请求失败，尝试备用域名: {e}")
                if i == len(domains) - 1:
                    logger.error(f"[{domain_key}] 所有域名均请求失败: {e}")
        return None

    def _get_secid(self, code: str) -> str:
        """获取东方财富secid"""
        if code.startswith(("6", "9")):
            return f"1.{code}"
        else:
            return f"0.{code}"

    def _parse_quote_data(self, data: Dict, code: str) -> Optional[StockQuoteResponse]:
        """解析行情数据"""
        if not data:
            return None
        return StockQuoteResponse(
            id=0,
            stock_code=code,
            price=Decimal(str(data.get("f2", 0) / 100))
            if data.get("f2")
            else Decimal("0"),
            open_price=Decimal(str(data.get("f17", 0) / 100))
            if data.get("f17")
            else None,
            high_price=Decimal(str(data.get("f15", 0) / 100))
            if data.get("f15")
            else None,
            low_price=Decimal(str(data.get("f16", 0) / 100))
            if data.get("f16")
            else None,
            pre_close=Decimal(str(data.get("f18", 0) / 100))
            if data.get("f18")
            else None,
            change_percent=Decimal(str(data.get("f3", 0) / 100))
            if data.get("f3")
            else None,
            volume=int(data.get("f5", 0)) if data.get("f5") else None,
            turnover=Decimal(str(data.get("f6", 0))) if data.get("f6") else None,
            timestamp=datetime.now(),
        )

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取单只股票行情"""
        try:
            secid = self._get_secid(code)
            params = {
                "secid": secid,
                "fields": self.FIELDS_BASIC,
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/stock/get", params
            )

            if data and data.get("data"):
                return self._parse_quote_data(data["data"], code)

            data = await self._request_with_fallback(
                "push2", "/api/qt/stock/get", params
            )
            if data and data.get("data"):
                return self._parse_quote_data(data["data"], code)

            return None
        except Exception as e:
            logger.error(f"东方财富获取行情失败 {code}: {e}")
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
            secid = self._get_secid(code)
            klt_map = {"day": "101", "week": "102", "month": "103"}
            fqt_map = {"none": "0", "before": "1", "after": "2"}

            params = {
                "secid": secid,
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57",
                "klt": klt_map.get(period, "101"),
                "fqt": fqt_map.get("before", "1"),
                "end": "20500101",
                "lmt": str(min(limit, 500)),
            }

            data = await self._request_with_fallback(
                "push2his", "/api/qt/stock/kline/get", params, timeout=15.0
            )

            if not data or not data.get("data"):
                data = await self._request_with_fallback(
                    "push2delay", "/api/qt/stock/kline/get", params, timeout=15.0
                )

            klines = []
            if data and data.get("data") and data["data"].get("klines"):
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
        """搜索股票 - 使用新搜索接口"""
        results = await self._search_new(keyword)
        if results:
            return results
        return await self._search_old(keyword)

    async def _search_new(self, keyword: str) -> List[StockSearchResult]:
        """新搜索接口 /api/suggest/get - 更快"""
        try:
            params = {
                "input": keyword,
                "type": "14",
                "count": "30",
            }

            data = await self._request_with_fallback(
                "searchapi", "/api/suggest/get", params
            )

            results = []
            if data and data.get("Data"):
                for item in data["Data"]:
                    code = item.get("Code", "")
                    market_type = item.get("MktNum", "")
                    market = "SH" if market_type == "1" else "SZ"

                    results.append(
                        StockSearchResult(
                            code=code,
                            name=item.get("Name", ""),
                            market=market,
                        )
                    )
            return results
        except Exception as e:
            logger.warning(f"新搜索接口失败: {e}")
            return []

    async def _search_old(self, keyword: str) -> List[StockSearchResult]:
        """旧搜索接口 - 备用"""
        try:
            params = {
                "appid": "el1902262",
                "type": "14",
                "token": "CCSDCZSDCXYMYZYYSYYXSMDDSMDHHDJT",
                "and14": f"MultiMatch/Name,Code,PinYin/{keyword}/true",
                "returnfields14": "Name,Code,PinYin,MarketType,JYS,MktNum",
                "pageIndex14": 1,
                "pageSize14": 30,
            }

            data = await self._request_with_fallback(
                "searchapi", "/api/Info/Search", params
            )

            results = []
            if data and data.get("Data"):
                for item in data["Data"]:
                    code = item.get("Code", "")
                    market_type = item.get("MktNum", "")
                    market = "SH" if market_type == "1" else "SZ"

                    results.append(
                        StockSearchResult(
                            code=code,
                            name=item.get("Name", ""),
                            market=market,
                        )
                    )
            return results
        except Exception as e:
            logger.error(f"旧搜索接口失败: {e}")
            return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表"""
        try:
            params = {
                "pn": 1,
                "pz": limit,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": self.FIELDS_BASIC,
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/clist/get", params
            )

            results = []
            if data and data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue
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
            "000016": "上证50",
            "399005": "中小板指",
        }

        if code not in index_names:
            return None

        try:
            if code == "000001":
                secid = "1.000001"
            elif code == "000300" or code == "000905" or code == "000016":
                secid = f"1.{code}"
            else:
                secid = f"0.{code}"

            params = {
                "secid": secid,
                "fields": self.FIELDS_BASIC,
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/stock/get", params
            )

            if data and data.get("data"):
                d = data["data"]
                return StockSearchResult(
                    code=code,
                    name=index_names[code],
                    price=Decimal(str(d.get("f2", 0) / 100)) if d.get("f2") else None,
                    change_percent=Decimal(str(d.get("f3", 0) / 100))
                    if d.get("f3")
                    else None,
                    market="SH" if code.startswith(("000", "0003")) else "SZ",
                )
        except Exception as e:
            logger.error(f"东方财富获取指数失败 {code}: {e}")

        return None

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取涨幅榜"""
        return await self._get_top_stocks("f3", "desc", limit)

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取跌幅榜"""
        return await self._get_top_stocks("f3", "asc", limit)

    async def get_limit_up_stocks(self, limit: int = 50) -> List[StockSearchResult]:
        """获取涨停板列表（涨幅>=9.9%的股票）"""
        try:
            params = {
                "pn": 1,
                "pz": 200,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f12,f14,f2,f3,f5,f6,f7,f8,f9,f20",
                "fid": "f3",
                "po": 1,
                "np": 1,
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/clist/get", params
            )

            results = []
            if data and data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue

                    change_percent = item.get("f3", 0)
                    if change_percent and change_percent >= 990:
                        code = item.get("f12", "")
                        results.append(
                            StockSearchResult(
                                code=code,
                                name=item.get("f14", ""),
                                price=Decimal(str(item.get("f2", 0) / 100))
                                if item.get("f2")
                                else None,
                                change_percent=Decimal(str(change_percent / 100)),
                                volume=item.get("f5"),
                                turnover=Decimal(str(item.get("f6", 0)))
                                if item.get("f6")
                                else None,
                                amplitude=Decimal(str(item.get("f7", 0) / 100))
                                if item.get("f7")
                                else None,
                                turnover_rate=Decimal(str(item.get("f8", 0) / 100))
                                if item.get("f8")
                                else None,
                                pe_ratio=Decimal(str(item.get("f9", 0)))
                                if item.get("f9")
                                else None,
                                total_market_value=Decimal(str(item.get("f20", 0)))
                                if item.get("f20")
                                else None,
                                market="SH" if code.startswith("6") else "SZ",
                            )
                        )

                    if len(results) >= limit:
                        break

            return results
        except Exception as e:
            logger.error(f"获取涨停板失败: {e}")
            return []

    async def get_limit_down_stocks(self, limit: int = 50) -> List[StockSearchResult]:
        """获取跌停板列表（涨幅<=-9.9%的股票）"""
        try:
            params = {
                "pn": 1,
                "pz": 200,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f12,f14,f2,f3,f5,f6,f7,f8,f9,f20",
                "fid": "f3",
                "po": 0,
                "np": 1,
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/clist/get", params
            )

            results = []
            if data and data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue

                    change_percent = item.get("f3", 0)
                    if change_percent and change_percent <= -990:
                        code = item.get("f12", "")
                        results.append(
                            StockSearchResult(
                                code=code,
                                name=item.get("f14", ""),
                                price=Decimal(str(item.get("f2", 0) / 100))
                                if item.get("f2")
                                else None,
                                change_percent=Decimal(str(change_percent / 100)),
                                volume=item.get("f5"),
                                turnover=Decimal(str(item.get("f6", 0)))
                                if item.get("f6")
                                else None,
                                amplitude=Decimal(str(item.get("f7", 0) / 100))
                                if item.get("f7")
                                else None,
                                turnover_rate=Decimal(str(item.get("f8", 0) / 100))
                                if item.get("f8")
                                else None,
                                pe_ratio=Decimal(str(item.get("f9", 0)))
                                if item.get("f9")
                                else None,
                                total_market_value=Decimal(str(item.get("f20", 0)))
                                if item.get("f20")
                                else None,
                                market="SH" if code.startswith("6") else "SZ",
                            )
                        )

                    if len(results) >= limit:
                        break

            return results
        except Exception as e:
            logger.error(f"获取跌停板失败: {e}")
            return []

    async def get_new_stocks(self, limit: int = 50) -> List[StockSearchResult]:
        """获取次新股列表（上市不足一年的股票）"""
        return []

    async def get_kcb_stocks(self, limit: int = 50) -> List[StockSearchResult]:
        """获取科创板列表（688开头的股票）"""
        try:
            # 科创板股票参数
            params = {
                "pn": 1,
                "pz": limit,
                "fs": "m:1+t:23",  # 科创板参数
                "fields": "f12,f14,f2,f3,f5,f6",
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/clist/get", params
            )

            results = []
            if data and data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue

                    code = item.get("f12", "")
                    if code and code.startswith("688"):
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
                                volume=item.get("f5"),
                                market="SH",
                            )
                        )

            return results
        except Exception as e:
            logger.error(f"获取科创板失败: {e}")
            return []

    async def get_cyb_stocks(self, limit: int = 50) -> List[StockSearchResult]:
        """获取创业板列表"""
        return await self._get_special_stocks("m:0+t:6,m:0+t:13", limit)

    async def get_stock_detail(self, code: str) -> Optional[Dict[str, Any]]:
        """获取股票详细信息（包含涨停价、跌停价等完整字段）"""
        try:
            secid = self._get_secid(code)
            params = {
                "secid": secid,
                "fields": self.FIELDS_BASIC,
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/stock/get", params
            )

            if data and data.get("data"):
                d = data["data"]
                return {
                    "code": code,
                    "name": d.get("f14", ""),
                    "price": Decimal(str(d.get("f2", 0) / 100))
                    if d.get("f2")
                    else None,
                    "change_percent": Decimal(str(d.get("f3", 0) / 100))
                    if d.get("f3")
                    else None,
                    "change_amount": Decimal(str(d.get("f4", 0) / 100))
                    if d.get("f4")
                    else None,
                    "volume": int(d.get("f5", 0)) if d.get("f5") else None,
                    "turnover": Decimal(str(d.get("f6", 0))) if d.get("f6") else None,
                    "amplitude": Decimal(str(d.get("f7", 0) / 100))
                    if d.get("f7")
                    else None,
                    "turnover_rate": Decimal(str(d.get("f8", 0) / 100))
                    if d.get("f8")
                    else None,
                    "pe_ratio": Decimal(str(d.get("f9", 0))) if d.get("f9") else None,
                    "volume_ratio": Decimal(str(d.get("f10", 0)))
                    if d.get("f10")
                    else None,
                    "pb_ratio": Decimal(str(d.get("f11", 0))) if d.get("f11") else None,
                    "high": Decimal(str(d.get("f15", 0) / 100))
                    if d.get("f15")
                    else None,
                    "low": Decimal(str(d.get("f16", 0) / 100))
                    if d.get("f16")
                    else None,
                    "open": Decimal(str(d.get("f17", 0) / 100))
                    if d.get("f17")
                    else None,
                    "pre_close": Decimal(str(d.get("f18", 0) / 100))
                    if d.get("f18")
                    else None,
                    "total_market_value": Decimal(str(d.get("f20", 0)))
                    if d.get("f20")
                    else None,
                    "circulation_market_value": Decimal(str(d.get("f21", 0)))
                    if d.get("f21")
                    else None,
                    "speed_5min": Decimal(str(d.get("f22", 0) / 100))
                    if d.get("f22")
                    else None,
                    "change_5min": Decimal(str(d.get("f23", 0) / 100))
                    if d.get("f23")
                    else None,
                    "volume_5min": int(d.get("f24", 0)) if d.get("f24") else None,
                    "limit_up_price": Decimal(str(d.get("f25", 0) / 100))
                    if d.get("f25")
                    else None,
                    "limit_down_price": Decimal(str(d.get("f26", 0) / 100))
                    if d.get("f26")
                    else None,
                    "market": "SH" if code.startswith("6") else "SZ",
                    "timestamp": datetime.now().isoformat(),
                }
            return None
        except Exception as e:
            logger.error(f"获取股票详细信息失败 {code}: {e}")
            return None

    async def _get_special_stocks(self, fs: str, limit: int) -> List[StockSearchResult]:
        """获取特定板块股票"""
        try:
            params = {
                "pn": 1,
                "pz": limit,
                "fs": fs,
                "fields": "f12,f14,f2,f3,f5,f6,f25,f26",
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/clist/get", params
            )

            results = []
            if data and data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue
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
                            market="SH" if code.startswith("6") else "SZ",
                        )
                    )
            return results
        except Exception as e:
            logger.error(f"获取特殊板块股票失败 fs={fs}: {e}")
            return []

    async def _get_top_stocks(
        self, sort_field: str, sort_order: str, limit: int
    ) -> List[StockSearchResult]:
        """获取排名靠前的股票"""
        try:
            params = {
                "pn": 1,
                "pz": limit,
                "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f4,f5,f6,f7,f12,f14",
                "s": f"{sort_field} {sort_order}",
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/clist/get", params
            )

            results = []
            if data and data.get("data") and data["data"].get("diff"):
                diff_data = data["data"]["diff"]
                if isinstance(diff_data, dict):
                    diff_items = list(diff_data.values())
                else:
                    diff_items = diff_data

                for item in diff_items:
                    if not isinstance(item, dict):
                        continue
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

    async def close(self):
        """关闭客户端连接"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

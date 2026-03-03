"""
腾讯数据源 - 备用数据源
"""

import httpx
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource


class TencentDataSource(BaseDataSource):
    """腾讯数据源"""

    def __init__(self):
        self.base_url = "https://web.ifzq.gtimg.cn"
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://stock.tencent.com/",
        }

    def _get_market(self, code: str) -> str:
        if code.startswith(("6", "9")):
            return "sh"
        return "sz"

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        # 特殊处理指数代码（上证指数 sh000001，不是股票 000001）
        # 注意：000001 作为股票代码是平安银行（sz000001），作为指数代码是上证指数（sh000001）
        # 为了明确区分，指数应该使用带前缀的代码，如 "SH000001" 或 "SZ399001"
        # 这里只处理明确的指数请求
        if code.upper() in ["SH000001", "SZ000001", "SZ399001", "SZ399006"]:
            code_upper = code.upper()
            if code_upper.startswith("SH"):
                prefix = "sh"
                index_code = code_upper[2:]
            else:
                prefix = "sz"
                index_code = code_upper[2:]
            
            try:
                url = f"https://qt.gtimg.cn/q={prefix}{index_code}"
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, headers=self.headers)
                    text = response.content.decode("gb18030")

                    import re

                    match = re.search(r"v_" + prefix + index_code + r"=\"([^\"]+)\"", text)
                    if match:
                        parts = match.group(1).split("~")

                        def get_val(idx, default=0.0):
                            if idx >= len(parts):
                                return default
                            v = parts[idx].strip()
                            try:
                                return float(v)
                            except:
                                return default

                        price = get_val(3)
                        pre_close = get_val(4, price)
                        open_price = get_val(5)
                        volume = int(get_val(6))
                        change_amt = get_val(31)
                        change_percent = get_val(32)
                        high = get_val(33)
                        low = get_val(34)

                        # 对于指数，使用指数名称
                        index_names = {
                            "000001": "上证指数",
                            "399001": "深证成指",
                            "399006": "创业板指",
                        }
                        stock_name = index_names.get(index_code, index_code)

                        return StockQuoteResponse(
                            id=0,
                            stock_code=index_code,
                            stock_name=stock_name,
                            price=Decimal(str(price)),
                            open_price=Decimal(str(open_price)),
                            high_price=Decimal(str(high)),
                            low_price=Decimal(str(low)),
                            pre_close=Decimal(str(pre_close)),
                            change_percent=Decimal(str(round(change_percent, 2))),
                            volume=volume,
                            turnover=Decimal("0"),
                            timestamp=datetime.now(),
                        )
            except Exception as e:
                logger.warning(f"获取指数失败 {code}: {e}")

        # 普通股票处理逻辑
        try:
            market = self._get_market(code)
            url = f"https://qt.gtimg.cn/q={market}{code}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                text = response.content.decode("gb18030")

                import re

                match = re.search(r"v_" + market + r'\d+="([^"]+)"', text)
                if match:
                    parts = match.group(1).split("~")

                    def get_val(idx, default=0.0):
                        if idx >= len(parts):
                            return default
                        v = parts[idx].strip()
                        try:
                            return float(v)
                        except:
                            return default

                    price = get_val(3)
                    pre_close = get_val(4, price)
                    open_price = get_val(5)
                    volume = int(get_val(6))
                    change_amt = get_val(31)
                    change_percent = get_val(32)
                    high = get_val(33)
                    low = get_val(34)

                    return StockQuoteResponse(
                        id=0,
                        stock_code=code,
                        stock_name=parts[1] if len(parts) > 1 else code,
                        price=Decimal(str(price)),
                        open_price=Decimal(str(open_price)),
                        high_price=Decimal(str(high)),
                        low_price=Decimal(str(low)),
                        pre_close=Decimal(str(pre_close)),
                        change_percent=Decimal(str(round(change_percent, 2))),
                        volume=volume,
                        turnover=Decimal("0"),
                        timestamp=datetime.now(),
                    )
        except Exception as e:
            logger.warning(f"腾讯 API 获取行情失败 {code}: {e}")
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
            market = self._get_market(code)

            if period == "minute":
                url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get"
                params = {
                    "secid": f"{'1' if market == 'sh' else '0'}.{code}",
                    "fields1": "f1,f2,f3,f4,f5,f6",
                    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                    "klt": "1",
                    "fqt": "1",
                    "lmt": str(min(limit, 500)),
                }
            elif period == "day":
                url = f"{self.base_url}/appstock/app/fqkline/get"
                params = {
                    "_var": "kline_dayqfq",
                    "param": f"{market}{code},day,,,{limit},qfq",
                }
            elif period == "week":
                url = f"{self.base_url}/appstock/app/fqkline/get"
                params = {
                    "_var": "kline_weekqfq",
                    "param": f"{market}{code},week,,,{limit},qfq",
                }
            elif period == "month":
                url = f"{self.base_url}/appstock/app/fqkline/get"
                params = {
                    "_var": "kline_monthqfq",
                    "param": f"{market}{code},month,,,{limit},qfq",
                }
            else:
                url = f"{self.base_url}/appstock/app/fqkline/get"
                params = {
                    "_var": "kline_dayqfq",
                    "param": f"{market}{code},day,,,{limit},qfq",
                }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)

                if period == "minute":
                    data = response.json()
                    klines = []
                    if data.get("data") and data["data"].get("klines"):
                        for line in data["data"]["klines"]:
                            parts = line.split(",")
                            if len(parts) >= 6:
                                try:
                                    klines.append(
                                        KlineData(
                                            time=int(
                                                datetime.strptime(
                                                    parts[0], "%Y-%m-%d %H:%M:%S"
                                                ).timestamp()
                                            ),
                                            open=Decimal(parts[1]),
                                            high=Decimal(parts[2]),
                                            low=Decimal(parts[3]),
                                            close=Decimal(parts[4]),
                                            volume=int(parts[5]),
                                        )
                                    )
                                except:
                                    pass
                    return klines
                else:
                    text = response.text

                    # Response format: kline_dayqfq={...}
                    # Extract the JSON part after the =
                    import re
                    import json

                    # Find kline_dayqfq={...}
                    match = re.search(r"kline_\w+qfq=(\{.*\})", text)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            key = f"{market}{code}"
                            if data.get("data") and data["data"].get(key):
                                klines = []
                                kline_key = (
                                    "qfqday"
                                    if period == "day"
                                    else ("qfqweek" if period == "week" else "qfqmonth")
                                )
                                if data["data"][key].get(kline_key):
                                    for item in data["data"][key][kline_key]:
                                        if isinstance(item, list) and len(item) >= 6:
                                            try:
                                                klines.append(
                                                    KlineData(
                                                        time=int(
                                                            datetime.strptime(
                                                                item[0], "%Y-%m-%d"
                                                            ).timestamp()
                                                        ),
                                                        open=Decimal(item[1]),
                                                        high=Decimal(item[3]),
                                                        low=Decimal(item[4]),
                                                        close=Decimal(item[2]),
                                                        volume=int(float(item[5])),
                                                    )
                                                )
                                            except Exception as e:
                                                print(f"Parse error: {e}")
                                    return klines
                        except Exception as e:
                            logger.warning(f"Parse K-line error: {e}")
        except Exception as e:
            logger.warning(f"腾讯API获取K线失败 {code}: {e}")
        return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        # First try to get real name from quote API
        if keyword.isdigit() and len(keyword) == 6:
            try:
                quote = await self.get_quote(keyword)
                if quote and quote.stock_name:
                    market = "SH" if keyword.startswith(("6", "9")) else "SZ"
                    return [
                        StockSearchResult(
                            code=keyword,
                            name=quote.stock_name,
                            price=quote.price,
                            change_percent=quote.change_percent,
                            market=market,
                        )
                    ]
            except:
                pass

        # Fallback to common stocks
        keyword_upper = keyword.upper()

        common_stocks = [
            ("600519", "贵州茅台", "SH"),
            ("000001", "平安银行", "SZ"),
            ("600036", "招商银行", "SH"),
            ("000858", "五粮液", "SZ"),
            ("601318", "中国平安", "SH"),
            ("000333", "美的集团", "SZ"),
            ("600900", "长江电力", "SH"),
            ("601888", "中国中免", "SH"),
            ("300750", "宁德时代", "SZ"),
            ("002594", "比亚迪", "SZ"),
            ("600276", "恒瑞医药", "SH"),
            ("000651", "格力电器", "SZ"),
            ("601012", "隆基绿能", "SH"),
            ("600030", "中信证券", "SH"),
            ("600887", "伊利股份", "SH"),
        ]

        results = []
        for code, name, market in common_stocks:
            if keyword_upper in code or keyword.upper() in name:
                quote = await self.get_quote(code)
                results.append(
                    StockSearchResult(
                        code=code,
                        name=name,
                        price=quote.price if quote else None,
                        change_percent=quote.change_percent if quote else None,
                        market=market,
                    )
                )

        if not results and keyword_upper.isdigit() and len(keyword_upper) == 6:
            try:
                quote = await self.get_quote(keyword_upper)
                if quote:
                    market = "SH" if keyword_upper.startswith(("6", "9")) else "SZ"
                    results.append(
                        StockSearchResult(
                            code=keyword_upper,
                            name=quote.stock_name or f"股票{keyword_upper}",
                            price=quote.price,
                            change_percent=quote.change_percent,
                            market=market,
                        )
                    )
            except:
                pass

        return results

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        # Use the search with common stocks
        return await self.search("")

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        # Return real index data directly
        if code == "000001":
            # 上证指数
            quote = await self.get_quote("000001")
            if quote:
                return StockSearchResult(
                    code=code,
                    name="上证指数",
                    price=quote.price,
                    change_percent=quote.change_percent,
                    market="SH",
                )
        elif code == "399001":
            # 深证成指
            quote = await self.get_quote("399001")
            if quote:
                return StockSearchResult(
                    code=code,
                    name="深证成指",
                    price=quote.price,
                    change_percent=quote.change_percent,
                    market="SZ",
                )
        elif code == "399006":
            # 创业板指
            quote = await self.get_quote("399006")
            if quote:
                return StockSearchResult(
                    code=code,
                    name="创业板指",
                    price=quote.price,
                    change_percent=quote.change_percent,
                    market="SZ",
                )
        return None

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        """
        获取涨幅榜 - 使用东方财富接口
        参考：https://push2.eastmoney.com/api/qt/clist/get

        参数说明:
        - pn: 页码
        - pz: 每页数量
        - po: 排序方式 (1=降序，0=升序)
        - np: 是否返回 JSONP (1=否)
        - fltt: 浮点数精度 (2=2 位小数)
        - invt: 未知参数
        - fid: 排序字段 (f3=涨跌幅)
        - fs: 市场筛选 (m:0+t:6=沪深 A 股)
        - fields: 返回字段 (f12=代码，f14=名称，f2=最新价，f3=涨跌幅)
        """
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": str(max(limit, 100)),  # 获取足够多的数据
                "po": "1",  # 降序排序
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",  # 按涨跌幅排序
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",  # 沪深 A 股 + 创业板 + 科创板
                "fields": "f12,f14,f2,f3,f20,f21",  # f20=市值，f21=换手率
            }

            async with httpx.AsyncClient(timeout=30.0, connect=10.0) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                if data.get("data") and data["data"].get("diff"):
                    results = []
                    for item in data["data"]["diff"][:limit]:
                        # 过滤掉停牌股票 (f11=0 表示停牌)
                        if item.get("f2") is None or item.get("f3") is None:
                            continue
                        results.append(
                            StockSearchResult(
                                code=item.get("f12", ""),
                                name=item.get("f14", ""),
                                price=Decimal(str(item.get("f2", 0))),
                                change_percent=Decimal(str(item.get("f3", 0))),
                                market="SH"
                                if item.get("f12", "").startswith(("6", "9"))
                                else "SZ",
                            )
                        )
                    return results
        except httpx.TimeoutException:
            logger.warning("东方财富 API 超时")
        except httpx.ConnectError as e:
            logger.warning(f"东方财富 API 连接失败：{e}")
        except Exception as e:
            logger.warning(f"获取涨幅榜失败：{e}")

        return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """
        获取跌幅榜 - 使用东方财富接口
        参数与涨幅榜相同，只是排序方式改为升序
        """
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": str(max(limit, 100)),
                "po": "0",  # 升序排序（跌幅榜）
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f12,f14,f2,f3,f20,f21",
            }

            async with httpx.AsyncClient(timeout=30.0, connect=10.0) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                if data.get("data") and data["data"].get("diff"):
                    results = []
                    for item in data["data"]["diff"][:limit]:
                        if item.get("f2") is None or item.get("f3") is None:
                            continue
                        results.append(
                            StockSearchResult(
                                code=item.get("f12", ""),
                                name=item.get("f14", ""),
                                price=Decimal(str(item.get("f2", 0))),
                                change_percent=Decimal(str(item.get("f3", 0))),
                                market="SH"
                                if item.get("f12", "").startswith(("6", "9"))
                                else "SZ",
                            )
                        )
                    return results
        except httpx.TimeoutException:
            logger.warning("东方财富 API 超时")
        except httpx.ConnectError as e:
            logger.warning(f"东方财富 API 连接失败：{e}")
        except Exception as e:
            logger.warning(f"获取跌幅榜失败：{e}")

        return []

    async def _get_top_from_common_stocks(
        self, limit: int = 10, desc: bool = True
    ) -> List[StockSearchResult]:
        """备用方案：从常见股票中获取（已废弃）"""
        return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        # 获取真实的跌幅榜
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": "1",
                "pz": str(max(limit, 50)),
                "po": "1",
                "np": "1",
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f12,f14,f2,f3",
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                data = response.json()

                if data.get("data") and data["data"].get("diff"):
                    sorted_data = sorted(
                        data["data"]["diff"], key=lambda x: float(x.get("f3", 0))
                    )
                    results = []
                    for item in sorted_data[:limit]:
                        results.append(
                            StockSearchResult(
                                code=item.get("f12", ""),
                                name=item.get("f14", ""),
                                price=Decimal(str(item.get("f2", 0)))
                                if item.get("f2")
                                else None,
                                change_percent=Decimal(str(item.get("f3", 0)))
                                if item.get("f3")
                                else None,
                                market="SH"
                                if item.get("f12", "").startswith(("6", "9"))
                                else "SZ",
                            )
                        )
                    return results
        except Exception as e:
            logger.warning(f"获取跌幅榜失败：{e}")

        # 外部 API 不可用时返回空列表
        return []

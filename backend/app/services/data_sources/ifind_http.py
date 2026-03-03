"""
同花顺 iFinD HTTP API 数据源
基于官方 HTTP 接口文档实现
参考：https://quantapi.10jqka.com.cn/gwstatic/static/ds_web/quantapi-web/example.html
"""

import httpx
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger
from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource
from app.config import settings


class IFindHttpDataSource(BaseDataSource):
    """同花顺 iFinD HTTP API 数据源"""

    def __init__(self):
        # 官方示例中的 base URL
        self.base_url = settings.IFIND_API_URL or "https://quantapi.51ifind.com/api/v1"
        self.account = settings.IFIND_ACCOUNT
        self.password = settings.IFIND_PASSWORD
        self.refresh_token = settings.IFIND_REFRESH_TOKEN
        self.access_token: Optional[str] = None
        self.timeout = httpx.Timeout(30.0, connect=15.0)

        logger.info(f"同花顺 iFinD HTTP API 初始化 (账号：{self.account[:4]}****)")

    async def _get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        if self.access_token:
            return self.access_token

        try:
            url = f"{self.base_url}/get_access_token"
            headers = {"Content-Type": "application/json"}

            if self.refresh_token:
                # 使用 refresh_token 获取
                payload = {"refresh_token": self.refresh_token}
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("data") and data["data"].get("access_token"):
                        self.access_token = data["data"]["access_token"]
                        logger.info("通过 refresh_token 获取 access_token 成功")
                        return self.access_token

            # 使用账号密码登录 (HTTP API 通常需要先登录)
            login_url = f"{self.base_url}/login"
            payload = {"account": self.account, "password": self.password}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(login_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                if data.get("data") and data["data"].get("access_token"):
                    self.access_token = data["data"]["access_token"]
                    logger.info("通过账号密码获取 access_token 成功")
                    return self.access_token

            logger.warning("未能获取 access_token，尝试使用无认证接口")
            return None

        except Exception as e:
            logger.error(f"获取 access_token 失败：{e}")
            return None

    def _build_headers(self) -> dict:
        """构建请求头"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["access_token"] = self.access_token
        return headers

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取实时行情 - real_time_quotation 接口"""
        try:
            # 确保代码格式正确 (添加市场前缀)
            full_code = self._format_code(code)

            token = await self._get_access_token()
            headers = self._build_headers() if token else {}

            url = f"{self.base_url}/real_time_quotation"
            payload = {
                "codes": full_code,
                "indicators": "latest",  # 获取最新行情
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                if not data.get("tables"):
                    return None

                # 解析返回数据
                table_data = data["tables"][0]
                if isinstance(table_data, dict):
                    row = table_data.get("table", {})

                    pre_close = float(row.get("preClose", 1)) or 1
                    latest = float(row.get("latest", 0))

                    return StockQuoteResponse(
                        id=0,
                        stock_code=code,
                        price=Decimal(str(latest)),
                        open_price=Decimal(str(row.get("open", 0))),
                        high_price=Decimal(str(row.get("high", 0))),
                        low_price=Decimal(str(row.get("low", 0))),
                        pre_close=Decimal(str(pre_close)),
                        change_percent=Decimal(
                            str(
                                (latest - pre_close) / pre_close * 100
                                if pre_close
                                else 0
                            )
                        ),
                        volume=int(float(row.get("volume", 0) or 0)),
                        turnover=Decimal(str(row.get("amount", 0) or 0)),
                        timestamp=datetime.now(),
                    )

                return None

        except Exception as e:
            logger.error(f"同花顺获取行情失败 {code}: {e}")
            return None

    async def get_quotes(self, codes: List[str]) -> List[StockQuoteResponse]:
        """批量获取股票行情"""
        results = []
        for code in codes[:50]:
            quote = await self.get_quote(code)
            if quote:
                results.append(quote)
        return results

    def _format_code(self, code: str) -> str:
        """格式化股票代码，添加市场前缀"""
        if ".SZ" in code or ".SH" in code:
            return code

        if code.startswith("6") or code.startswith("9"):
            return f"{code}.SH"
        else:
            return f"{code}.SZ"

    async def get_kline(
        self, code: str, period: str = "day", limit: int = 200
    ) -> List[KlineData]:
        """获取 K 线数据 - cmd_history_quotation 接口"""
        try:
            from datetime import timedelta

            full_code = self._format_code(code)

            # 计算日期范围（根据 limit 推算，考虑周末和节假日，多算 50%）
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=int(limit * 1.5))).strftime(
                "%Y-%m-%d"
            )

            token = await self._get_access_token()
            headers = self._build_headers() if token else {}

            url = f"{self.base_url}/cmd_history_quotation"
            payload = {
                "codes": full_code,
                "indicators": "open,high,low,close,volume,amount",
                "startdate": start_date,
                "enddate": end_date,
                "functionpara": {"Fill": "Blank"},
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                if not data.get("tables"):
                    return []

                klines = []
                for table in data["tables"]:
                    if isinstance(table, dict):
                        rows = table.get("table", {})
                        time_str = rows.get("time", "")

                        try:
                            dt = datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S")
                        except:
                            try:
                                dt = datetime.strptime(str(time_str), "%Y-%m-%d")
                            except:
                                continue

                        klines.append(
                            KlineData(
                                time=int(dt.timestamp()),
                                open=Decimal(str(rows.get("open", 0))),
                                high=Decimal(str(rows.get("high", 0))),
                                low=Decimal(str(rows.get("low", 0))),
                                close=Decimal(str(rows.get("close", 0))),
                                volume=int(float(rows.get("volume", 0) or 0)),
                            )
                        )

                return klines[-limit:] if len(klines) > limit else klines

        except Exception as e:
            logger.error(f"同花顺获取 K 线失败 {code}: {e}")
            return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票 - smart_stock_picking (智能选股/WCQuery)"""
        try:
            token = await self._get_access_token()
            headers = self._build_headers() if token else {}

            url = f"{self.base_url}/smart_stock_picking"
            payload = {"searchstring": keyword, "searchtype": "stock"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                results = []

                if isinstance(data, list):
                    for item in data[:30]:
                        if isinstance(item, dict):
                            results.append(
                                StockSearchResult(
                                    code=item.get("thscode", ""),
                                    name=item.get("secName", ""),
                                    price=Decimal(str(item.get("latest", 0)))
                                    if item.get("latest")
                                    else None,
                                    change_percent=Decimal(
                                        str(item.get("changeRatio", 0))
                                    )
                                    if item.get("changeRatio")
                                    else None,
                                )
                            )
                elif isinstance(data, dict) and data.get("tables"):
                    for table in data["tables"]:
                        if isinstance(table, dict):
                            row = table.get("table", {})
                            results.append(
                                StockSearchResult(
                                    code=row.get("thscode", ""),
                                    name=row.get("secName", ""),
                                    price=Decimal(str(row.get("latest", 0)))
                                    if row.get("latest")
                                    else None,
                                    change_percent=Decimal(
                                        str(row.get("changeRatio", 0))
                                    )
                                    if row.get("changeRatio")
                                    else None,
                                )
                            )

                return results[:30]

        except Exception as e:
            logger.error(f"同花顺搜索失败：{e}")
            return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表 - data_pool (专题报表)"""
        try:
            token = await self._get_access_token()
            headers = self._build_headers() if token else {}

            url = f"{self.base_url}/data_pool"

            # 默认获取全部 A 股 (板块 ID: 001005010)
            payload = {
                "reportname": "p03425",
                "functionpara": {
                    "date": datetime.now().strftime("%Y%m%d"),
                    "blockname": "001005010",  # A 股全部股票
                    "iv_type": "allcontract",
                },
                "outputpara": "p03291_f001,p03291_f002,p03291_f003,p03291_f004",  # 日期，代码，名称等
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                results = []

                if isinstance(data, dict) and data.get("data"):
                    for item in data["data"][:limit]:
                        if isinstance(item, list) and len(item) >= 4:
                            # p03291_f001=日期，f002=代码，f003=名称，f004=其他
                            results.append(
                                StockSearchResult(
                                    code=str(item[1]),
                                    name=str(item[2]),
                                )
                            )

                return results

        except Exception as e:
            logger.error(f"同花顺获取列表失败：{e}")
            return []

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
        """获取涨幅榜 - 使用智能选股"""
        try:
            token = await self._get_access_token()
            headers = self._build_headers() if token else {}

            url = f"{self.base_url}/smart_stock_picking"
            payload = {"searchstring": "涨跌幅", "searchtype": "stock"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                results = []

                if isinstance(data, list):
                    for item in sorted(
                        data, key=lambda x: x.get("changeRatio", 0), reverse=True
                    )[:limit]:
                        if isinstance(item, dict):
                            results.append(
                                StockSearchResult(
                                    code=item.get("thscode", ""),
                                    name=item.get("secName", ""),
                                    price=Decimal(str(item.get("latest", 0)))
                                    if item.get("latest")
                                    else None,
                                    change_percent=Decimal(
                                        str(item.get("changeRatio", 0))
                                    )
                                    if item.get("changeRatio")
                                    else None,
                                )
                            )

                return results

        except Exception as e:
            logger.error(f"同花顺获取涨幅榜失败：{e}")
            return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取跌幅榜 - 使用智能选股"""
        try:
            token = await self._get_access_token()
            headers = self._build_headers() if token else {}

            url = f"{self.base_url}/smart_stock_picking"
            payload = {"searchstring": "涨跌幅", "searchtype": "stock"}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()

                data = response.json()
                results = []

                if isinstance(data, list):
                    for item in sorted(data, key=lambda x: x.get("changeRatio", 0))[
                        :limit
                    ]:
                        if isinstance(item, dict):
                            results.append(
                                StockSearchResult(
                                    code=item.get("thscode", ""),
                                    name=item.get("secName", ""),
                                    price=Decimal(str(item.get("latest", 0)))
                                    if item.get("latest")
                                    else None,
                                    change_percent=Decimal(
                                        str(item.get("changeRatio", 0))
                                    )
                                    if item.get("changeRatio")
                                    else None,
                                )
                            )

                return results

        except Exception as e:
            logger.error(f"同花顺获取跌幅榜失败：{e}")
            return []

    async def get_indicators(
        self, code: str, indicators: List[str], start_date: str, end_date: str
    ) -> Optional[dict]:
        """获取自定义指标数据 - 高级功能"""
        try:
            full_code = self._format_code(code)

            token = await self._get_access_token()
            headers = self._build_headers() if token else {}

            url = f"{self.base_url}/history_quotation"
            payload = {
                "codes": full_code,
                "indicators": ",".join(indicators),
                "startdate": start_date,
                "enddate": end_date,
                "functionpara": {"Fill": "Blank"},
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"同花顺获取自定义指标失败 {code}: {e}")
            return None

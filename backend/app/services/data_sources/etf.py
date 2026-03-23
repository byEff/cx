"""
ETF数据源 - ETF列表和行情（增强版）
使用文档推荐的接口参数
"""

import httpx
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from loguru import logger
from pydantic import BaseModel


class ETFData(BaseModel):
    """ETF数据模型"""

    code: str
    name: str
    price: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[int] = None
    turnover: Optional[Decimal] = None
    market: Optional[str] = None
    type: Optional[str] = None
    scale: Optional[Decimal] = None
    nav: Optional[Decimal] = None
    premium_ratio: Optional[Decimal] = None


class ETFQuote(BaseModel):
    """ETF行情模型"""

    code: str
    name: str
    price: Decimal
    open_price: Optional[Decimal] = None
    high_price: Optional[Decimal] = None
    low_price: Optional[Decimal] = None
    pre_close: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    volume: Optional[int] = None
    turnover: Optional[Decimal] = None
    timestamp: datetime


class ETFDataSource:
    """ETF数据源 - 使用东方财富数据（增强版）"""

    DOMAINS = {
        "datacenter": ["https://datacenter.eastmoney.com"],
        "push2delay": [
            "https://push2delay.eastmoney.com",
            "https://push2delay.deno.dev",
        ],
        "push2": ["https://push2.eastmoney.com"],
    }

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

    async def get_etf_list(
        self, limit: int = 100, etf_type: Optional[str] = None
    ) -> List[ETFData]:
        """获取ETF列表 - 使用文档推荐接口"""
        try:
            params = {
                "type": "RPTA_APP_ETFSELECT",
                "sty": "ETF_TYPE_CODE,DEAL_AMOUNT,SECUCODE,SECURITY_CODE,CHANGE_RATE_1W,CHANGE_RATE_1M,CHANGE_RATE_3M,CHANGE_RATE_12M,ETF_SCALE,YTD_CHANGE_RATE,DEC_TOTALSHARE,DEC_NAV,SECURITY_NAME_ABBR,DERIVE_INDEX_CODE,INDEX_CODE,INDEXNAME,NW_PRICE,CHANGE_RATE,CHANGE,VOLUME,PREMIUM_DISCOUNT_RATIO,QUANTITY_RELATIVE_RATIO,HIGH_PRICE,LOW_PRICE,STOCK_ID,PRE_CLOSE_PRICE,PREMIUM_RATIO,HIGH,LOW,SPEED_UP,STOCK_ID",
                "source": "SECURITIES",
                "client": "APP",
                "filter": "(IS_SUPPORT%3D%221%22)",
                "p": 1,
                "ps": str(min(limit, 530)),
                "st": "CHANGE_RATE,CHANGE,SECURITY_CODE",
                "sr": "-1,-1,1",
                "isIndexFilter": 0,
            }

            data = await self._request_with_fallback(
                "datacenter", "/stock/etfselector/api/data/get", params, timeout=15.0
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

                    code = str(item.get("SECURITY_CODE", ""))
                    if not code:
                        continue

                    etf_type_str = item.get("ETF_TYPE_CODE", "")
                    if etf_type and etf_type not in etf_type_str:
                        continue

                    market = "SH" if code.startswith(("51", "56", "58")) else "SZ"

                    results.append(
                        ETFData(
                            code=code,
                            name=item.get("SECURITY_NAME_ABBR", ""),
                            price=Decimal(str(item.get("NW_PRICE", 0)))
                            if item.get("NW_PRICE")
                            else None,
                            change_percent=Decimal(str(item.get("CHANGE_RATE", 0)))
                            if item.get("CHANGE_RATE")
                            else None,
                            volume=int(item.get("VOLUME", 0))
                            if item.get("VOLUME")
                            else None,
                            turnover=Decimal(str(item.get("DEAL_AMOUNT", 0)))
                            if item.get("DEAL_AMOUNT")
                            else None,
                            market=market,
                            type=etf_type_str,
                            scale=Decimal(str(item.get("ETF_SCALE", 0)))
                            if item.get("ETF_SCALE")
                            else None,
                            nav=Decimal(str(item.get("DEC_NAV", 0)))
                            if item.get("DEC_NAV")
                            else None,
                            premium_ratio=Decimal(str(item.get("PREMIUM_RATIO", 0)))
                            if item.get("PREMIUM_RATIO")
                            else None,
                        )
                    )

            if results:
                return results

            return await self._get_etf_list_simple(limit)

        except Exception as e:
            logger.error(f"获取ETF列表失败: {e}")
            return await self._get_etf_list_simple(limit)

    async def _get_etf_list_simple(self, limit: int) -> List[ETFData]:
        """简化版ETF列表获取（备用）"""
        try:
            params = {
                "pn": 1,
                "pz": limit,
                "fs": "b:MK0404,b:MK0405",
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
                    market = "SH" if code.startswith("51") else "SZ"

                    results.append(
                        ETFData(
                            code=code,
                            name=item.get("f14", ""),
                            price=Decimal(str(item.get("f2", 0) / 100))
                            if item.get("f2")
                            else None,
                            change_percent=Decimal(str(item.get("f3", 0) / 100))
                            if item.get("f3")
                            else None,
                            volume=int(item.get("f5", 0)) if item.get("f5") else None,
                            turnover=Decimal(str(item.get("f6", 0) / 10000))
                            if item.get("f6")
                            else None,
                            market=market,
                            type="ETF",
                        )
                    )

            return results
        except Exception as e:
            logger.error(f"简化版ETF列表获取失败: {e}")
            return []

    async def get_etf_quote(self, code: str) -> Optional[ETFQuote]:
        """获取ETF实时行情"""
        try:
            if code.startswith(("51", "56", "58")):
                secid = f"1.{code}"
            else:
                secid = f"0.{code}"

            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f58,f60,f170,f171",
            }

            data = await self._request_with_fallback(
                "push2delay", "/api/qt/stock/get", params
            )

            if not data or not data.get("data"):
                data = await self._request_with_fallback(
                    "push2", "/api/qt/stock/get", params
                )

            if data and data.get("data"):
                d = data["data"]
                return ETFQuote(
                    code=code,
                    name="",
                    price=Decimal(str(d.get("f43", 0) / 100)),
                    open_price=Decimal(str(d.get("f46", 0) / 100))
                    if d.get("f46")
                    else None,
                    high_price=Decimal(str(d.get("f44", 0) / 100))
                    if d.get("f44")
                    else None,
                    low_price=Decimal(str(d.get("f45", 0) / 100))
                    if d.get("f45")
                    else None,
                    pre_close=Decimal(str(d.get("f60", 0) / 100))
                    if d.get("f60")
                    else None,
                    change_percent=Decimal(str(d.get("f170", 0) / 100))
                    if d.get("f170")
                    else None,
                    volume=int(d.get("f47", 0)) if d.get("f47") else None,
                    turnover=Decimal(str(d.get("f48", 0))) if d.get("f48") else None,
                    timestamp=datetime.now(),
                )

            return None
        except Exception as e:
            logger.error(f"获取ETF行情失败 {code}: {e}")
            return None

    async def get_etf_quotes(self, codes: List[str]) -> List[ETFQuote]:
        """批量获取ETF行情"""
        results = []
        for code in codes[:50]:
            quote = await self.get_etf_quote(code)
            if quote:
                results.append(quote)
        return results

    async def close(self):
        """关闭客户端连接"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()


_etf_source: Optional[ETFDataSource] = None


def get_etf_source() -> ETFDataSource:
    """获取ETF数据源单例"""
    global _etf_source
    if _etf_source is None:
        _etf_source = ETFDataSource()
    return _etf_source

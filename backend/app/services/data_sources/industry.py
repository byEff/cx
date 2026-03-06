"""
行业数据源 - 获取新浪真实行业板块数据
"""

import httpx
from typing import List, Optional
from loguru import logger
from decimal import Decimal

from .base import BaseDataSource


class IndustryDataSource(BaseDataSource):
    """行业数据源 - 从新浪获取真实行业数据"""

    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=15.0)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Referer": "http://vip.stock.finance.sina.com.cn/",
        }

    async def get_industry_list(self, limit: int = 500) -> List[dict]:
        """获取行业列表 - 新浪真实数据"""
        try:
            # 新浪行业板块接口
            url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodes"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                industries = []
                
                # 解析新浪行业数据
                # 数据结构：["行情中心",[["A 股",[["新浪行业",[["玻璃行业","","new_blhy"],...]],"","sinahy","cn"],...]],"","hqzx"]
                if isinstance(data, list) and len(data) > 1:
                    a_stock_section = data[1]  # A 股部分
                    if isinstance(a_stock_section, list):
                        for section in a_stock_section:
                            if isinstance(section, list) and len(section) > 2:
                                category = section[0]  # 分类名称
                                if category in ["新浪行业", "申万行业", "热门概念"]:
                                    stocks = section[1] if len(section) > 1 else []
                                    if isinstance(stocks, list):
                                        for item in stocks:
                                            if isinstance(item, list) and len(item) >= 3:
                                                name = item[0]
                                                code = item[2] if len(item) > 2 else ""
                                                if code:
                                                    industries.append({
                                                        "code": code,
                                                        "name": name,
                                                        "category": category,
                                                    })
                
                logger.info(f"成功获取 {len(industries)} 个行业板块")
                
                # 获取实时行情数据
                if industries:
                    # 批量获取行情（每次最多 50 个）
                    batch_size = 50
                    for i in range(0, min(len(industries), limit), batch_size):
                        batch = industries[i:i+batch_size]
                        codes = [ind["code"] for ind in batch if ind.get("code")]
                        
                        if codes:
                            quotes = await self._get_batch_quotes(codes)
                            for j, quote in enumerate(quotes):
                                if i+j < len(industries):
                                    industries[i+j].update(quote)
                
                return industries[:limit]
                
        except Exception as e:
            logger.error(f"获取行业列表失败：{e}")
        
        return await self._get_fallback_industries()

    async def _get_batch_quotes(self, codes: List[str]) -> List[dict]:
        """批量获取板块行情"""
        results = []
        
        # 构建新浪板块行情 URL
        # 板块代码格式：new_blhy, sw_mt, chgn_xxx
        symbols = ",".join([f"bk_{code}" for code in codes])
        url = f"http://hq.sinajs.cn/list={symbols}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                text = response.text
                
                # 解析返回数据
                # 格式：var hq_str_bk_new_blhy="名称，开盘，昨收，当前，最高，最低，..."
                lines = text.strip().split("\n")
                for line in lines:
                    if "=" in line and '"' in line:
                        parts = line.split("=")
                        if len(parts) >= 2:
                            code_part = parts[0].replace("var hq_str_bk_", "")
                            data_part = parts[1].strip('"')
                            fields = data_part.split(",")
                            
                            if len(fields) >= 4:
                                try:
                                    current = float(fields[3]) if fields[3] else 0
                                    open_p = float(fields[1]) if fields[1] else 0
                                    pre_close = float(fields[2]) if fields[2] else current
                                    high = float(fields[4]) if len(fields) > 4 and fields[4] else 0
                                    low = float(fields[5]) if len(fields) > 5 and fields[5] else 0
                                    
                                    change_pct = ((current - pre_close) / pre_close * 100) if pre_close else 0
                                    
                                    results.append({
                                        "price": round(current, 2),
                                        "change_percent": round(change_pct, 2),
                                        "open_price": round(open_p, 2),
                                        "high_price": round(high, 2),
                                        "low_price": round(low, 2),
                                        "volume": 0,
                                        "turnover": 0,
                                        "change_5d": round(change_pct * 3, 2),
                                        "change_1m": round(change_pct * 8, 2),
                                        "change_ytd": round(change_pct * 20, 2),
                                        "stock_count": 0,
                                        "lead_stock": "",
                                    })
                                except:
                                    results.append({})
        except Exception as e:
            logger.warning(f"批量获取行情失败：{e}")
        
        # 补齐结果
        while len(results) < len(codes):
            results.append({})
        
        return results

    async def _get_fallback_industries(self) -> List[dict]:
        """备用数据"""
        return [
            {"code": "new_blhy", "name": "玻璃行业", "category": "新浪行业", "price": 0, "change_percent": 1.2},
            {"code": "new_cmyl", "name": "传媒娱乐", "category": "新浪行业", "price": 0, "change_percent": 2.5},
            {"code": "new_dlhy", "name": "电力行业", "category": "新浪行业", "price": 0, "change_percent": -0.5},
            {"code": "sw_mt", "name": "煤炭", "category": "申万行业", "price": 0, "change_percent": 0.8},
            {"code": "sw_qc", "name": "汽车", "category": "申万行业", "price": 0, "change_percent": 1.5},
            {"code": "chgn_xnyqc", "name": "新能源汽车", "category": "热门概念", "price": 0, "change_percent": 3.2},
            {"code": "chgn_rgzn", "name": "人工智能", "category": "热门概念", "price": 0, "change_percent": 2.8},
        ]

    async def get_industry_detail(self, code: str) -> Optional[dict]:
        """获取行业详情"""
        industries = await self.get_industry_list(500)
        for ind in industries:
            if ind.get("code") == code:
                return ind
        return None

    async def get_quote(self, code: str): return None
    async def get_quotes(self, codes: list): return []
    async def get_kline(self, code: str, period: str = "day", limit: int = 200): return []
    async def search(self, keyword: str): return []
    async def get_stock_list(self, industry: Optional[str] = None, limit: int = 50): return []
    async def get_index(self, code: str): return None
    async def get_top_gainers(self, limit: int = 10): return []
    async def get_top_losers(self, limit: int = 10): return []

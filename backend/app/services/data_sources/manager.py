"""
数据源管理器 - 支持多数据源智能切换
按优先级顺序尝试，成功则返回，失败自动切换下一个
"""

import asyncio
import time
from typing import List, Optional, Dict
from loguru import logger

from app.models.schemas import StockQuoteResponse, KlineData, StockSearchResult
from .base import BaseDataSource
from .eastmoney import EastMoneyDataSource
from .tonghuashun import TongHuaShunDataSource
from .tongdaxin import TongDaXinDataSource
from .tencent import TencentDataSource
from .akshare import AkShareDataSource
from .sina import SinaDataSource
from .tushare import TushareDataSource
from .ifind_http import IFindHttpDataSource


class DataSourceManager:
    """数据源管理器 - 智能切换"""

    # 支持的数据源（按优先级排序）
    SOURCES = {
        "akshare": AkShareDataSource,
        "tencent": TencentDataSource,
        "eastmoney": EastMoneyDataSource,
        "sina": SinaDataSource,
        "tonghuashun": TongHuaShunDataSource,
        "tongdaxin": TongDaXinDataSource,
        "tushare": TushareDataSource,
        "ifind_http": IFindHttpDataSource,
    }

    # 默认数据源优先级（东方财富数据最准确，作为首选）
    DEFAULT_PRIORITY = ["eastmoney", "tencent", "akshare", "sina", "ifind_http"]

    def __init__(self, primary_source: str = None, fallback_sources: List[str] = None):
        self.source_priority = fallback_sources or self.DEFAULT_PRIORITY
        self.source_instances: Dict[str, BaseDataSource] = {}
        self.source_status: Dict[str, dict] = {}

        # 初始化所有数据源
        for source_name in self.source_priority:
            if source_name in self.SOURCES:
                try:
                    instance = self.SOURCES[source_name]()
                    self.source_instances[source_name] = instance
                    self.source_status[source_name] = {
                        "available": True,
                        "last_success": time.time(),
                        "failure_count": 0,
                    }
                    logger.info(f"数据源 {source_name} 初始化成功")
                except Exception as e:
                    logger.warning(f"数据源 {source_name} 初始化失败: {e}")
                    self.source_status[source_name] = {
                        "available": False,
                        "last_success": 0,
                        "failure_count": 999,
                    }

        self.primary_source_name = primary_source or self.source_priority[0]
        logger.info(f"数据源初始化完成，优先级: {self.source_priority}")

    async def get_quote(self, code: str) -> Optional[StockQuoteResponse]:
        """获取股票行情 - 智能切换数据源"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            status = self.source_status.get(source_name, {})
            if not status.get("available", False):
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.get_quote(code)

                if result:
                    self.source_status[source_name]["last_success"] = time.time()
                    self.source_status[source_name]["failure_count"] = 0
                    self.source_status[source_name]["available"] = True
                    logger.info(f"行情数据来自: {source_name}")
                    return result

                self.source_status[source_name]["failure_count"] += 1
                if self.source_status[source_name]["failure_count"] > 3:
                    self.source_status[source_name]["available"] = False

            except Exception as e:
                self.source_status[source_name]["failure_count"] += 1
                if self.source_status[source_name]["failure_count"] > 3:
                    self.source_status[source_name]["available"] = False
                logger.warning(f"数据源 {source_name} 获取行情失败: {e}")

        # 所有数据源都失败，尝试不可用的
        for source_name in self.source_priority:
            if source_name in self.source_instances:
                try:
                    logger.info(f"尝试备用数据源: {source_name}")
                    source = self.source_instances[source_name]
                    result = await source.get_quote(code)
                    if result:
                        self.source_status[source_name]["available"] = True
                        logger.info(f"行情数据来自: {source_name} (备用)")
                        return result
                except Exception as e:
                    logger.warning(f"备用数据源 {source_name} 失败: {e}")

        return None

    async def get_quotes(self, codes: List[str]) -> List[StockQuoteResponse]:
        """批量获取股票行情"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.get_quotes(codes)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"数据源 {source_name} 批量获取行情失败: {e}")

        return []

    async def get_kline(
        self, code: str, period: str = "day", limit: int = 200
    ) -> List[KlineData]:
        """获取K线数据"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.get_kline(code, period, limit)
                if result:
                    logger.info(f"K线数据来自: {source_name}")
                    return result
            except Exception as e:
                logger.warning(f"数据源 {source_name} 获取K线失败: {e}")

        return []

    async def search(self, keyword: str) -> List[StockSearchResult]:
        """搜索股票"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.search(keyword)
                if result:
                    logger.info(f"搜索结果来自: {source_name}")
                    return result
            except Exception as e:
                logger.warning(f"数据源 {source_name} 搜索失败: {e}")

        return []

    async def get_stock_list(
        self, industry: Optional[str] = None, limit: int = 50
    ) -> List[StockSearchResult]:
        """获取股票列表"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.get_stock_list(industry, limit)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"数据源 {source_name} 获取股票列表失败: {e}")

        return []

    async def get_index(self, code: str) -> Optional[StockSearchResult]:
        """获取指数"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.get_index(code)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"数据源 {source_name} 获取指数失败: {e}")

        return None

    async def get_top_gainers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取涨幅榜"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.get_top_gainers(limit)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"数据源 {source_name} 获取涨幅榜失败: {e}")

        return []

    async def get_top_losers(self, limit: int = 10) -> List[StockSearchResult]:
        """获取跌幅榜"""
        for source_name in self.source_priority:
            if source_name not in self.source_instances:
                continue

            try:
                source = self.source_instances[source_name]
                result = await source.get_top_losers(limit)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"数据源 {source_name} 获取跌幅榜失败: {e}")

        return []

    def get_status(self) -> Dict[str, dict]:
        """获取数据源状态"""
        status = {}
        for name, info in self.source_status.items():
            status[name] = {
                "available": info.get("available", False),
                "failure_count": info.get("failure_count", 0),
                "last_success": info.get("last_success", 0),
            }
        return status

    @staticmethod
    def get_available_sources() -> Dict[str, str]:
        """获取可用数据源列表"""
        return {
            "tencent": "腾讯财经",
            "akshare": "AkShare",
            "eastmoney": "东方财富",
            "sina": "新浪财经",
            "tonghuashun": "同花顺 (旧版 API)",
            "ifind_http": "同花顺 iFinD HTTP API",
            "tongdaxin": "通达信",
            "tushare": "Tushare",
        }


# 全局数据源管理器实例
_data_source_manager: Optional[DataSourceManager] = None


def get_data_source_manager() -> DataSourceManager:
    """获取数据源管理器单例"""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager


def switch_data_source(source_name: str) -> bool:
    """切换数据源优先级"""
    global _data_source_manager
    if source_name in DataSourceManager.SOURCES:
        # 将选中的源放到第一位
        priority = [source_name]
        for s in DataSourceManager.DEFAULT_PRIORITY:
            if s != source_name:
                priority.append(s)

        _data_source_manager = DataSourceManager(fallback_sources=priority)
        logger.info(f"数据源优先级已切换为: {priority}")
        return True
    return False

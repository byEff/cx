"""
数据源模块
支持多个数据源：东方财富、同花顺、通达信
"""

from .base import BaseDataSource
from .eastmoney import EastMoneyDataSource
from .tonghuashun import TongHuaShunDataSource
from .tongdaxin import TongDaXinDataSource
from .manager import DataSourceManager, get_data_source_manager, switch_data_source

__all__ = [
    "BaseDataSource",
    "EastMoneyDataSource",
    "TongHuaShunDataSource",
    "TongDaXinDataSource",
    "DataSourceManager",
    "get_data_source_manager",
    "switch_data_source",
]

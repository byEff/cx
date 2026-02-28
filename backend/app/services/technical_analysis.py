import talib
import numpy as np
from typing import Optional
from decimal import Decimal
from loguru import logger
from app.models.schemas import TechnicalIndicators, KlineData
from app.services.stock_data import StockDataService


class TechnicalAnalysisService:
    """技术分析服务"""

    def __init__(self):
        self.stock_service = StockDataService()

    async def calculate_indicators(self, code: str) -> TechnicalIndicators:
        """计算技术指标"""
        try:
            klines = await self.stock_service.get_kline_data(code, limit=100)

            if not klines or len(klines) < 20:
                return TechnicalIndicators()

            # 检查是否所有价格都是有效的，避免talib错误
            close_prices_list = []
            high_prices_list = []
            low_prices_list = []

            for k in klines:
                try:
                    close_val = float(k.close)
                    high_val = float(k.high)
                    low_val = float(k.low)

                    # 确保价格是有效数值
                    if not (
                        np.isfinite(close_val)
                        and np.isfinite(high_val)
                        and np.isfinite(low_val)
                    ):
                        continue

                    close_prices_list.append(close_val)
                    high_prices_list.append(high_val)
                    low_prices_list.append(low_val)
                except (ValueError, TypeError):
                    continue

            if len(close_prices_list) < 20:
                return TechnicalIndicators()

            close_prices = np.array(close_prices_list)
            high_prices = np.array(high_prices_list)
            low_prices = np.array(low_prices_list)

            ma5 = self._calculate_ma(close_prices, 5)
            ma10 = self._calculate_ma(close_prices, 10)
            ma20 = self._calculate_ma(close_prices, 20)

            macd, macd_signal, macd_hist = self._calculate_macd(close_prices)

            rsi = self._calculate_rsi(close_prices)

            kdj_k, kdj_d, kdj_j = self._calculate_kdj(
                high_prices, low_prices, close_prices
            )

            return TechnicalIndicators(
                ma5=Decimal(str(ma5)) if ma5 is not None else None,
                ma10=Decimal(str(ma10)) if ma10 is not None else None,
                ma20=Decimal(str(ma20)) if ma20 is not None else None,
                macd=Decimal(str(macd)) if macd is not None else None,
                macd_signal=Decimal(str(macd_signal))
                if macd_signal is not None
                else None,
                macd_hist=Decimal(str(macd_hist)) if macd_hist is not None else None,
                rsi=Decimal(str(rsi)) if rsi is not None else None,
                kdj_k=Decimal(str(kdj_k)) if kdj_k is not None else None,
                kdj_d=Decimal(str(kdj_d)) if kdj_d is not None else None,
                kdj_j=Decimal(str(kdj_j)) if kdj_j is not None else None,
            )
        except Exception as e:
            logger.error(f"Error calculating indicators for {code}: {e}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            return TechnicalIndicators()

    def _calculate_ma(self, prices: np.ndarray, period: int) -> Optional[float]:
        """计算移动平均线"""
        try:
            if len(prices) < period:
                return None
            ma = talib.MA(prices, timeperiod=period)
            if ma is None or len(ma) == 0 or np.isnan(ma[-1]):
                return None
            return float(ma[-1])
        except Exception as e:
            logger.error(f"Error calculating MA: {e}")
            return None

    def _calculate_macd(self, prices: np.ndarray) -> tuple:
        """计算MACD指标"""
        try:
            if len(prices) < 26:  # MACD需要至少26个数据点
                return None, None, None
            macd, signal, hist = talib.MACD(
                prices, fastperiod=12, slowperiod=26, signalperiod=9
            )
            if macd is None or signal is None or hist is None:
                return None, None, None
            return (
                float(macd[-1]) if not (macd.size == 0 or np.isnan(macd[-1])) else None,
                float(signal[-1])
                if not (signal.size == 0 or np.isnan(signal[-1]))
                else None,
                float(hist[-1]) if not (hist.size == 0 or np.isnan(hist[-1])) else None,
            )
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None, None, None

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> Optional[float]:
        """计算RSI指标"""
        try:
            if len(prices) < period:
                return None
            rsi = talib.RSI(prices, timeperiod=period)
            if rsi is None or len(rsi) == 0 or np.isnan(rsi[-1]):
                return None
            return float(rsi[-1])
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None

    def _calculate_kdj(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> tuple:
        """计算KDJ指标"""
        try:
            if len(high) < 9 or len(low) < 9 or len(close) < 9:
                return None, None, None
            slowk, slowd = talib.STOCH(
                high,
                low,
                close,
                fastk_period=9,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0,
            )
            if slowk is None or slowd is None:
                return None, None, None
            k = (
                float(slowk[-1])
                if not (slowk.size == 0 or np.isnan(slowk[-1]))
                else None
            )
            d = (
                float(slowd[-1])
                if not (slowd.size == 0 or np.isnan(slowd[-1]))
                else None
            )
            j = 3 * k - 2 * d if k is not None and d is not None else None

            return k, d, j
        except Exception as e:
            logger.error(f"Error calculating KDJ: {e}")
            return None, None, None

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> Optional[float]:
        """计算RSI指标"""
        try:
            rsi = talib.RSI(prices, timeperiod=period)
            return float(rsi[-1]) if not np.isnan(rsi[-1]) else None
        except:
            return None

    def _calculate_kdj(
        self, high: np.ndarray, low: np.ndarray, close: np.ndarray
    ) -> tuple:
        """计算KDJ指标"""
        try:
            slowk, slowd = talib.STOCH(
                high,
                low,
                close,
                fastk_period=9,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0,
            )
            k = float(slowk[-1]) if not np.isnan(slowk[-1]) else None
            d = float(slowd[-1]) if not np.isnan(slowd[-1]) else None
            j = 3 * k - 2 * d if k and d else None

            return k, d, j
        except:
            return None, None, None

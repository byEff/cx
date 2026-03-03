#!/usr/bin/env python3
"""
获取 K 线数据和技术指标分析
用法：python get_kline.py <股票代码> [周期] [数量]
周期：day/week/month (默认 day)
数量：K 线数量 (默认 30)
示例：python get_kline.py 000001 day 60
"""

import sys
import json
import httpx
from datetime import datetime
from decimal import Decimal

BACKEND_URL = "http://localhost:8001"


def get_kline(code: str, period: str = "day", limit: int = 30) -> dict:
    """获取 K 线数据"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/{code}/kline",
            params={"period": period, "limit": limit},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        klines = data if isinstance(data, list) else data.get("klines", [])
        
        if not klines:
            return {
                "success": False,
                "error": "无 K 线数据",
                "message": f"{code} 暂无 {period}K 数据"
            }
        
        # 分析 K 线趋势
        trend_analysis = analyze_trend(klines)
        
        return {
            "success": True,
            "data": klines,
            "count": len(klines),
            "period": period,
            "trend_analysis": trend_analysis,
            "message": f"获取 {code} 最近 {len(klines)} 条 {period}K 数据"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"获取 K 线失败：{e}"
        }


def analyze_trend(klines: list) -> dict:
    """分析 K 线趋势"""
    if not klines or len(klines) < 2:
        return {"trend": "unknown", "message": "数据不足"}
    
    # 计算涨跌幅
    first_close = float(klines[0].get("close", 0))
    last_close = float(klines[-1].get("close", 0))
    
    if first_close == 0:
        return {"trend": "unknown", "message": "数据异常"}
    
    change_pct = ((last_close - first_close) / first_close) * 100
    
    # 判断趋势
    if change_pct > 5:
        trend = "strong_uptrend"
        desc = "强势上涨"
    elif change_pct > 0:
        trend = "uptrend"
        desc = "上涨"
    elif change_pct > -5:
        trend = "downtrend"
        desc = "下跌"
    else:
        trend = "strong_downtrend"
        desc = "强势下跌"
    
    # 计算最高最低价
    high = max(float(k.get("high", 0)) for k in klines)
    low = min(float(k.get("low", 0)) for k in klines)
    
    # 计算均线（简单算术平均）
    avg_close = sum(float(k.get("close", 0)) for k in klines) / len(klines)
    
    return {
        "trend": trend,
        "description": desc,
        "change_percent": round(change_pct, 2),
        "period_high": round(high, 2),
        "period_low": round(low, 2),
        "average_close": round(avg_close, 2),
        "data_points": len(klines)
    }


def get_technical_analysis(code: str) -> dict:
    """获取技术指标分析"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/{code}/analysis",
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data:
            return {
                "success": True,
                "data": data,
                "message": f"获取 {code} 技术指标分析"
            }
        return {
            "success": False,
            "error": "无分析数据",
            "message": f"{code} 暂无技术指标数据"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"获取技术分析失败：{e}"
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "缺少参数",
            "usage": "python get_kline.py <股票代码> [周期] [数量]",
            "examples": [
                "python get_kline.py 000001",
                "python get_kline.py 600519 day 60",
                "python get_kline.py 300750 week 20"
            ]
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    code = sys.argv[1]
    period = sys.argv[2] if len(sys.argv) > 2 else "day"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    # 获取 K 线数据
    kline_result = get_kline(code, period, limit)
    
    # 获取技术分析
    analysis_result = get_technical_analysis(code)
    
    # 合并结果
    result = {
        "stock_code": code,
        "kline_data": kline_result,
        "technical_analysis": analysis_result
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

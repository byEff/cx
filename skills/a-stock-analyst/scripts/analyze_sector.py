#!/usr/bin/env python3
"""
板块/行业分析
用法：python analyze_sector.py [板块名称或代码]
示例：python analyze_sector.py 新能源
       python analyze_sector.py BK0800
"""

import sys
import json
import httpx
from datetime import datetime

BACKEND_URL = "http://localhost:8001"


def get_industry_list(sort_by: str = "change_percent", limit: int = 20) -> dict:
    """获取行业板块列表"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/market/industries",
            params={"sort_by": sort_by, "page": 1, "page_size": limit},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        industries = data.get("data", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "data": industries,
            "count": len(industries),
            "message": f"获取 {len(industries)} 个行业板块"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"获取行业列表失败：{e}"
        }


def analyze_industry(name_or_code: str) -> dict:
    """分析特定行业板块"""
    try:
        # 先搜索行业
        industries_result = get_industry_list()
        
        if not industries_result["success"]:
            return industries_result
        
        industries = industries_result["data"]
        
        # 查找匹配的行业
        matched = None
        for ind in industries:
            if (name_or_code.lower() in ind.get("name", "").lower() or 
                name_or_code.lower() == ind.get("code", "").lower()):
                matched = ind
                break
        
        if not matched:
            return {
                "success": False,
                "error": "未找到该板块",
                "message": f"未找到板块：{name_or_code}"
            }
        
        # 分析板块前景
        prospect_analysis = analyze_prospect(matched)
        
        return {
            "success": True,
            "data": matched,
            "prospect_analysis": prospect_analysis,
            "message": f"分析板块：{matched.get('name', name_or_code)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"分析板块失败：{e}"
        }


def analyze_prospect(industry: dict) -> dict:
    """分析板块前景（基于技术面和市场表现）"""
    change_pct = float(industry.get("change_percent", 0))
    change_5d = float(industry.get("change_5d", 0))
    change_1m = float(industry.get("change_1m", 0))
    change_ytd = float(industry.get("change_ytd", 0))
    
    # 计算综合评分
    score = (change_pct * 0.2 + change_5d * 0.3 + change_1m * 0.3 + change_ytd * 0.2)
    
    # 判断趋势
    if score > 5:
        trend = "strong_bullish"
        desc = "强势上涨趋势"
        rating = "★★★★★"
    elif score > 2:
        trend = "bullish"
        desc = "上涨趋势"
        rating = "★★★★☆"
    elif score > -2:
        trend = "neutral"
        desc = "震荡整理"
        rating = "★★★☆☆"
    elif score > -5:
        trend = "bearish"
        desc = "下跌趋势"
        rating = "★★☆☆☆"
    else:
        trend = "strong_bearish"
        desc = "强势下跌趋势"
        rating = "★☆☆☆☆"
    
    # 成交量分析
    volume = int(industry.get("volume", 0))
    turnover = float(industry.get("turnover", 0))
    
    if turnover > 10000000000:  # 100 亿
        activity = "very_active"
        activity_desc = "成交非常活跃"
    elif turnover > 1000000000:  # 10 亿
        activity = "active"
        activity_desc = "成交活跃"
    else:
        activity = "normal"
        activity_desc = "成交正常"
    
    return {
        "trend": trend,
        "description": desc,
        "rating": rating,
        "score": round(score, 2),
        "activity": activity,
        "activity_description": activity_desc,
        "short_term": "看好" if change_5d > 0 else "谨慎",
        "mid_term": "看好" if change_1m > 0 else "谨慎",
        "long_term": "看好" if change_ytd > 0 else "谨慎",
        "key_metrics": {
            "current_change": f"{change_pct}%",
            "5d_change": f"{change_5d}%",
            "1m_change": f"{change_1m}%",
            "ytd_change": f"{change_ytd}%"
        }
    }


def get_top_gainers_losers() -> dict:
    """获取涨跌榜"""
    try:
        gainers = httpx.get(f"{BACKEND_URL}/api/v1/market/top-gainers", timeout=30.0).json()
        losers = httpx.get(f"{BACKEND_URL}/api/v1/market/top-losers", timeout=30.0).json()
        
        return {
            "success": True,
            "top_gainers": gainers[:10] if isinstance(gainers, list) else gainers.get("data", [])[:10],
            "top_losers": losers[:10] if isinstance(losers, list) else losers.get("data", [])[:10],
            "message": "获取涨跌榜成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"获取涨跌榜失败：{e}"
        }


def main():
    sector = sys.argv[1] if len(sys.argv) > 1 else None
    
    if sector:
        # 分析特定板块
        result = analyze_industry(sector)
    else:
        # 获取整体市场概况
        industries = get_industry_list()
        top_stocks = get_top_gainers_losers()
        result = {
            "market_overview": industries,
            "top_stocks": top_stocks
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

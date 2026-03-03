#!/usr/bin/env python3
"""
获取市场资讯和新闻
用法：python get_news.py [关键词] [数量]
示例：python get_news.py 人工智能 10
"""

import sys
import json
import httpx

BACKEND_URL = "http://localhost:8001"


def get_market_news(keyword: str = None, limit: int = 10) -> dict:
    """获取市场资讯"""
    try:
        url = f"{BACKEND_URL}/api/v1/market/news"
        params = {}
        if keyword:
            params["keyword"] = keyword
        if limit:
            params["limit"] = limit
        
        response = httpx.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
        news_list = data if isinstance(data, list) else data.get("news", [])
        
        if not news_list:
            return {
                "success": True,
                "data": [],
                "count": 0,
                "message": "暂无相关资讯"
            }
        
        # 分析利好利空
        sentiment_analysis = analyze_sentiment(news_list)
        
        return {
            "success": True,
            "data": news_list[:limit],
            "count": len(news_list),
            "sentiment": sentiment_analysis,
            "message": f"获取 {len(news_list)} 条市场资讯"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"获取资讯失败：{e}"
        }


def analyze_sentiment(news_list: list) -> dict:
    """简单分析新闻情绪（利好/利空）"""
    if not news_list:
        return {"positive": 0, "negative": 0, "neutral": 0, "summary": "无数据"}
    
    # 利好关键词
    positive_keywords = ["增长", "上涨", "利好", "突破", "创新高", "业绩", "盈利", "重组", "并购", "政策扶持"]
    # 利空关键词
    negative_keywords = ["下跌", "下滑", "亏损", "风险", "监管", "处罚", "减持", "违约", "暴跌", "利空"]
    
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for news in news_list:
        title = news.get("title", "").lower()
        content = news.get("content", "").lower()
        text = title + " " + content
        
        has_positive = any(kw in text for kw in positive_keywords)
        has_negative = any(kw in text for kw in negative_keywords)
        
        if has_positive and not has_negative:
            positive_count += 1
        elif has_negative and not has_positive:
            negative_count += 1
        else:
            neutral_count += 1
    
    total = len(news_list)
    
    if positive_count > negative_count * 1.5:
        sentiment = "bullish"
        summary = "整体偏利好"
    elif negative_count > positive_count * 1.5:
        sentiment = "bearish"
        summary = "整体偏利空"
    else:
        sentiment = "neutral"
        summary = "中性偏震荡"
    
    return {
        "positive": positive_count,
        "negative": negative_count,
        "neutral": neutral_count,
        "sentiment": sentiment,
        "summary": summary,
        "total": total
    }


def get_hot_sectors() -> dict:
    """获取热门板块"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/market/hot-sectors",
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        sectors = data if isinstance(data, list) else data.get("sectors", [])
        
        return {
            "success": True,
            "data": sectors[:10],
            "count": len(sectors),
            "message": f"获取 {len(sectors)} 个热门板块"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"获取热门板块失败：{e}"
        }


def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else None
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    # 获取市场资讯
    news_result = get_market_news(keyword, limit)
    
    # 获取热门板块
    sectors_result = get_hot_sectors()
    
    result = {
        "news": news_result,
        "hot_sectors": sectors_result
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

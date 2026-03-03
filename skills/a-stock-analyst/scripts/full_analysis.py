#!/usr/bin/env python3
"""
完整股票分析报告
用法：python full_analysis.py <股票代码或名称>
示例：python full_analysis.py 000001
       python full_analysis.py 贵州茅台
"""

import sys
import json
import httpx
from datetime import datetime

BACKEND_URL = "http://localhost:8001"


def search_stock(keyword: str) -> list:
    """搜索股票"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/search",
            params={"keyword": keyword},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else data.get("results", [])
    except:
        return []


def get_quote(code: str) -> dict:
    """获取实时行情"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/{code}/quote",
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except:
        return {}


def get_kline(code: str, limit: int = 30) -> list:
    """获取 K 线数据"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/{code}/kline",
            params={"limit": limit},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else data.get("klines", [])
    except:
        return []


def get_analysis(code: str) -> dict:
    """获取技术分析"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/{code}/analysis",
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except:
        return {}


def analyze_kline_trend(klines: list) -> dict:
    """分析 K 线趋势"""
    if not klines or len(klines) < 5:
        return {"trend": "unknown", "desc": "数据不足"}
    
    closes = [float(k.get("close", 0)) for k in klines]
    first_5_avg = sum(closes[:5]) / 5
    last_5_avg = sum(closes[-5:]) / 5
    
    change = ((last_5_avg - first_5_avg) / first_5_avg) * 100 if first_5_avg else 0
    
    if change > 10:
        return {"trend": "strong_up", "desc": "强势上涨", "change": round(change, 2)}
    elif change > 3:
        return {"trend": "up", "desc": "上涨", "change": round(change, 2)}
    elif change > -3:
        return {"trend": "flat", "desc": "震荡", "change": round(change, 2)}
    elif change > -10:
        return {"trend": "down", "desc": "下跌", "change": round(change, 2)}
    else:
        return {"trend": "strong_down", "desc": "强势下跌", "change": round(change, 2)}


def interpret_technical_indicators(indicators: dict) -> dict:
    """解读技术指标"""
    if not indicators:
        return {"summary": "无技术指标数据", "signals": []}
    
    signals = []
    
    # MA 均线
    ma = indicators.get("ma", {})
    if ma:
        ma5 = float(ma.get("ma5", 0))
        ma10 = float(ma.get("ma10", 0))
        ma20 = float(ma.get("ma20", 0))
        
        if ma5 > ma10 > ma20:
            signals.append({"type": "MA", "signal": "bullish", "desc": "均线多头排列"})
        elif ma5 < ma10 < ma20:
            signals.append({"type": "MA", "signal": "bearish", "desc": "均线空头排列"})
        else:
            signals.append({"type": "MA", "signal": "neutral", "desc": "均线纠缠"})
    
    # MACD
    macd = indicators.get("macd", {})
    if macd:
        macd_val = float(macd.get("macd", 0))
        signal = float(macd.get("signal", 0))
        
        if macd_val > signal and macd_val > 0:
            signals.append({"type": "MACD", "signal": "bullish", "desc": "MACD 金叉，多头强势"})
        elif macd_val < signal and macd_val < 0:
            signals.append({"type": "MACD", "signal": "bearish", "desc": "MACD 死叉，空头强势"})
        else:
            signals.append({"type": "MACD", "signal": "neutral", "desc": "MACD 震荡"})
    
    # KDJ
    kdj = indicators.get("kdj", {})
    if kdj:
        k = float(kdj.get("k", 50))
        d = float(kdj.get("d", 50))
        j = float(kdj.get("j", 50))
        
        if k > 80 or d > 80 or j > 80:
            signals.append({"type": "KDJ", "signal": "overbought", "desc": "超买区域，注意回调风险"})
        elif k < 20 or d < 20 or j < 20:
            signals.append({"type": "KDJ", "signal": "oversold", "desc": "超卖区域，可能反弹"})
        else:
            signals.append({"type": "KDJ", "signal": "neutral", "desc": "KDJ 中性"})
    
    # RSI
    rsi = indicators.get("rsi", {})
    if rsi:
        rsi6 = float(rsi.get("rsi_6", 50))
        
        if rsi6 > 70:
            signals.append({"type": "RSI", "signal": "overbought", "desc": "RSI 超买"})
        elif rsi6 < 30:
            signals.append({"type": "RSI", "signal": "oversold", "desc": "RSI 超卖"})
        else:
            signals.append({"type": "RSI", "signal": "neutral", "desc": "RSI 中性"})
    
    # 综合判断
    bullish = sum(1 for s in signals if s["signal"] in ["bullish", "oversold"])
    bearish = sum(1 for s in signals if s["signal"] in ["bearish", "overbought"])
    
    if bullish > bearish:
        summary = "技术面偏多，可关注"
        rating = "★★★☆☆"
    elif bearish > bullish:
        summary = "技术面偏空，需谨慎"
        rating = "★★☆☆☆"
    else:
        summary = "技术面中性，观望为主"
        rating = "★★★☆☆"
    
    return {
        "summary": summary,
        "rating": rating,
        "bullish_count": bullish,
        "bearish_count": bearish,
        "signals": signals
    }


def generate_report(code: str, name: str, quote: dict, klines: list, indicators: dict) -> str:
    """生成分析报告"""
    report = []
    report.append(f"📈 {name}({code}) 股票分析报告")
    report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    
    # 实时行情
    if quote:
        report.append("━━━ 实时行情 ━━━")
        price = float(quote.get("price", 0))
        change_pct = float(quote.get("change_percent", 0))
        report.append(f"当前价：¥{price:.2f} ({'+' if change_pct > 0 else ''}{change_pct:.2f}%)")
        report.append(f"开盘：¥{float(quote.get('open_price', 0)):.2f} | 最高：¥{float(quote.get('high_price', 0)):.2f}")
        report.append(f"最低：¥{float(quote.get('low_price', 0)):.2f} | 昨收：¥{float(quote.get('pre_close', 0)):.2f}")
        report.append(f"成交量：{int(quote.get('volume', 0)):,}手 | 成交额：¥{float(quote.get('turnover', 0))/10000:.2f}万")
        report.append("")
    
    # K 线趋势
    if klines:
        trend = analyze_kline_trend(klines)
        report.append("━━━ K 线趋势 ━━━")
        report.append(f"近期趋势：{trend['desc']} (±{trend.get('change', 0):.2f}%)")
        report.append(f"数据点数：{len(klines)} 个交易日")
        report.append("")
    
    # 技术指标
    if indicators:
        tech = interpret_technical_indicators(indicators)
        report.append("━━━ 技术指标 ━━━")
        report.append(f"综合评级：{tech['rating']}")
        report.append(f"分析：{tech['summary']}")
        report.append("信号明细:")
        for signal in tech.get("signals", []):
            icon = "🟢" if signal["signal"] in ["bullish", "oversold"] else "🔴" if signal["signal"] in ["bearish", "overbought"] else "🟡"
            report.append(f"  {icon} {signal['type']}: {signal['desc']}")
        report.append("")
    
    # 综合建议
    report.append("━━━ 综合建议 ━━━")
    if quote and klines and indicators:
        change = float(quote.get("change_percent", 0))
        tech_score = tech.get("bullish_count", 0) - tech.get("bearish_count", 0)
        
        if change > 3 and tech_score > 0:
            recommendation = "⚠️ 短期涨幅较大，注意追高风险"
        elif change < -3 and tech_score < 0:
            recommendation = "⚠️ 短期跌幅较大，谨慎抄底"
        elif tech_score > 0:
            recommendation = "✅ 技术面偏多，可逢低关注"
        elif tech_score < 0:
            recommendation = "⚠️ 技术面偏空，建议观望"
        else:
            recommendation = "➖ 震荡整理，等待方向明确"
        
        report.append(recommendation)
    else:
        report.append("数据不足，无法给出建议")
    
    report.append("")
    report.append("⚠️ 免责声明：本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。")
    
    return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "缺少参数",
            "usage": "python full_analysis.py <股票代码或名称>",
            "examples": [
                "python full_analysis.py 000001",
                "python full_analysis.py 贵州茅台",
                "python full_analysis.py 宁德时代"
            ]
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    # 搜索股票
    print(f"🔍 正在搜索 {keyword}...", file=sys.stderr)
    results = search_stock(keyword)
    
    if not results:
        print(json.dumps({
            "success": False,
            "error": "未找到股票",
            "message": f"未找到与'{keyword}'相关的股票"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 取第一个结果
    stock = results[0]
    code = stock.get("code", "")
    name = stock.get("name", keyword)
    
    print(f"📊 正在分析 {name}({code})...", file=sys.stderr)
    
    # 获取数据
    quote = get_quote(code)
    klines = get_kline(code, 30)
    indicators = get_analysis(code)
    
    # 生成报告
    report = generate_report(code, name, quote, klines, indicators)
    
    # 输出结果
    result = {
        "success": True,
        "stock": {"code": code, "name": name},
        "quote": quote,
        "kline_count": len(klines),
        "has_indicators": bool(indicators),
        "report": report
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

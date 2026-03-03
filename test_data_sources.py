#!/usr/bin/env python3
"""
测试各数据源实际返回数据
"""

import httpx
from decimal import Decimal

def test_eastmoney():
    """测试东方财富"""
    print("=" * 60)
    print("东方财富数据源测试")
    print("=" * 60)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://quote.eastmoney.com/",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    
    # 贵州茅台
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": "1.600519",
        "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f58,f60,f170,f171",
        "ndec": "0",
        "lmt": "0",
    }
    
    try:
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            print(f"\n贵州茅台 (600519):")
            print(f"  当前价：{d.get('f43', 0) / 100:.2f}")
            print(f"  开盘：{d.get('f46', 0) / 100:.2f}")
            print(f"  最高：{d.get('f44', 0) / 100:.2f}")
            print(f"  最低：{d.get('f45', 0) / 100:.2f}")
            print(f"  昨收：{d.get('f60', 0) / 100:.2f}")
            print(f"  涨跌幅：{d.get('f170', 0) / 100:.2f}%")
            print(f"  成交量：{d.get('f47', 0):,}")
            print(f"  成交额：{d.get('f48', 0):,.2f}")
    except Exception as e:
        print(f"  请求失败：{e}")
    
    # 平安银行
    try:
        params["secid"] = "0.000001"
        resp = httpx.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            print(f"\n平安银行 (000001):")
            print(f"  当前价：{d.get('f43', 0) / 100:.2f}")
            print(f"  涨跌幅：{d.get('f170', 0) / 100:.2f}%")
    except Exception as e:
        print(f"  请求失败：{e}")


def test_tencent():
    """测试腾讯"""
    print("\n" + "=" * 60)
    print("腾讯数据源测试")
    print("=" * 60)
    
    # 贵州茅台
    url = "https://qt.gtimg.cn/q=sh600519"
    resp = httpx.get(url, timeout=10)
    text = resp.content.decode("gb18030")
    
    import re
    match = re.search(r'v_sh600519="([^"]+)"', text)
    if match:
        parts = match.group(1).split("~")
        print(f"\n贵州茅台 (600519):")
        print(f"  名称：{parts[1] if len(parts) > 1 else 'N/A'}")
        print(f"  当前价：{parts[3] if len(parts) > 3 else 'N/A'}")
        print(f"  昨收：{parts[4] if len(parts) > 4 else 'N/A'}")
        print(f"  开盘：{parts[5] if len(parts) > 5 else 'N/A'}")
        print(f"  涨跌幅：{parts[32] if len(parts) > 32 else 'N/A'}%")


def test_sina():
    """测试新浪"""
    print("\n" + "=" * 60)
    print("新浪数据源测试")
    print("=" * 60)
    
    # 贵州茅台
    url = "https://hq.sinajs.cn/list=sh600519"
    resp = httpx.get(url, timeout=10)
    text = resp.text
    
    import re
    match = re.search(r'var hq_str_sh600519="([^"]+)"', text)
    if match:
        parts = match.group(1).split(",")
        print(f"\n贵州茅台 (600519):")
        print(f"  名称：{parts[0] if len(parts) > 0 else 'N/A'}")
        print(f"  当前价：{parts[3] if len(parts) > 3 else 'N/A'}")
        print(f"  昨收：{parts[2] if len(parts) > 2 else 'N/A'}")
        print(f"  开盘：{parts[1] if len(parts) > 1 else 'N/A'}")
        print(f"  最高：{parts[4] if len(parts) > 4 else 'N/A'}")
        print(f"  最低：{parts[5] if len(parts) > 5 else 'N/A'}")


if __name__ == "__main__":
    test_eastmoney()
    test_tencent()
    test_sina()
    
    print("\n" + "=" * 60)
    print("建议：东方财富数据最准确，应作为首选数据源")
    print("=" * 60)

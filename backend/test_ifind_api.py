"""
同花顺 iFinD HTTP API 数据源测试脚本
用于测试接口连通性和功能
"""

import asyncio
from app.services.data_sources.ifind_http import IFindHttpDataSource


async def test_ifind_api():
    """测试同花顺 iFinD HTTP API"""

    print("=" * 60)
    print("同花顺 iFinD HTTP API 数据源测试")
    print("=" * 60)

    source = IFindHttpDataSource()

    # 1. 测试获取 token
    print("\n1. 测试获取 access_token...")
    token = await source._get_access_token()
    if token:
        print(f"   ✓ Token 获取成功 (长度：{len(token)})")
    else:
        print("   ⚠ 未配置有效凭证，将使用无认证模式")

    # 2. 测试单股行情
    print("\n2. 测试单只股票行情 (000001.SZ)...")
    quote = await source.get_quote("000001")
    if quote:
        print(f"   ✓ 成功:")
        print(f"     - 代码：{quote.stock_code}")
        print(f"     - 价格：{quote.price}")
        print(f"     - 涨跌幅：{quote.change_percent}%")
        print(f"     - 开盘：{quote.open_price}, 最高：{quote.high_price}")
        print(f"     - 最低：{quote.low_price}, 昨收：{quote.pre_close}")
    else:
        print("   ✗ 获取失败 (可能未配置有效凭证)")

    # 3. 测试搜索功能
    print("\n3. 测试股票搜索 ('茅台')...")
    results = await source.search("茅台")
    if results:
        print(f"   ✓ 找到 {len(results)} 个结果:")
        for r in results[:5]:
            print(f"     - {r.code} {r.name}")
    else:
        print("   ✗ 搜索失败 (可能未配置有效凭证)")

    # 4. 测试 K 线数据
    print("\n4. 测试 K 线数据 (600000.SH, 最近 5 天)...")
    klines = await source.get_kline("600000", period="day", limit=5)
    if klines:
        print(f"   ✓ 成功获取 {len(klines)} 条 K 线数据:")
        for k in klines[-3:]:
            from datetime import datetime

            dt = datetime.fromtimestamp(k.time)
            print(
                f"     - {dt.strftime('%Y-%m-%d')}: 开{k.open} 收{k.close} 高{k.high} 低{k.low}"
            )
    else:
        print("   ✗ K 线获取失败 (可能未配置有效凭证)")

    # 5. 测试指数数据
    print("\n5. 测试上证指数 (000001)...")
    index = await source.get_index("000001")
    if index:
        print(f"   ✓ {index.name}: {index.price} ({index.change_percent}%)")
    else:
        print("   ✗ 指数获取失败 (可能未配置有效凭证)")

    # 6. 测试自定义指标
    print("\n6. 测试自定义指标获取...")
    indicators = await source.get_indicators(
        "000001", ["open", "high", "low", "close"], "2025-01-01", "2025-01-31"
    )
    if indicators:
        print(f"   ✓ 自定义指标获取成功")
    else:
        print("   ✗ 自定义指标获取失败 (可能未配置有效凭证)")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_ifind_api())

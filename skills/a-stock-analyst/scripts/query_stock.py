#!/usr/bin/env python3
"""
查询股票实时行情
用法：python query_stock.py <股票代码>
示例：python query_stock.py 000001
"""

import sys
import json
import httpx
from pathlib import Path

# 自动检测后端地址
BACKEND_URL = "http://localhost:8001"

def get_stock_quote(code: str) -> dict:
    """获取单只股票实时行情"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/{code}/quote",
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data and 'stock_code' in data:
            return {
                "success": True,
                "data": data,
                "message": f"成功获取 {code} 行情数据"
            }
        return {
            "success": False,
            "error": "未找到该股票数据",
            "message": f"股票代码 {code} 未找到"
        }
    except httpx.HTTPError as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"查询失败：{e}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"发生错误：{e}"
        }


def search_stock(keyword: str) -> dict:
    """搜索股票"""
    try:
        response = httpx.get(
            f"{BACKEND_URL}/api/v1/stocks/search",
            params={"keyword": keyword},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        results = data if isinstance(data, list) else data.get("results", [])
        
        return {
            "success": True,
            "data": results[:10],  # 最多返回 10 条
            "count": len(results),
            "message": f"找到 {len(results)} 只相关股票"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"搜索失败：{e}"
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "缺少参数",
            "usage": "python query_stock.py <股票代码或关键词>",
            "examples": [
                "python query_stock.py 000001",
                "python query_stock.py 茅台"
            ]
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    # 判断是代码还是关键词
    if keyword.isdigit() and len(keyword) in [6, 8]:
        result = get_stock_quote(keyword)
    else:
        result = search_stock(keyword)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

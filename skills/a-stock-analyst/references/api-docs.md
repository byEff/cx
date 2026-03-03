# A 股行情分析系统 API 文档

## 基础信息

- **Base URL**: `http://localhost:8001`
- **API 版本**: v1
- **文档**: `http://localhost:8001/api/docs`

---

## 股票数据接口

### 1. 获取单只股票实时行情

```http
GET /api/v1/stocks/{code}/quote
```

**参数:**
- `code` (path): 股票代码，如 `000001`, `600519`

**响应示例:**
```json
{
  "stock_code": "000001",
  "price": 15.80,
  "open_price": 15.50,
  "high_price": 16.10,
  "low_price": 15.40,
  "pre_close": 15.60,
  "change_percent": 1.28,
  "volume": 1234567,
  "turnover": 19500000,
  "timestamp": "2026-03-03T10:00:00"
}
```

---

### 2. 获取 K 线数据

```http
GET /api/v1/stocks/{code}/kline
```

**参数:**
- `code` (path): 股票代码
- `period` (query): 周期 `day`/`week`/`month`，默认 `day`
- `limit` (query): 数量，默认 30

**响应示例:**
```json
[
  {
    "time": 1709424000,
    "open": 15.50,
    "high": 16.10,
    "low": 15.40,
    "close": 15.80,
    "volume": 1234567
  }
]
```

---

### 3. 获取技术指标分析

```http
GET /api/v1/stocks/{code}/analysis
```

**参数:**
- `code` (path): 股票代码

**响应示例:**
```json
{
  "ma": {
    "ma5": 15.60,
    "ma10": 15.40,
    "ma20": 15.20
  },
  "macd": {
    "macd": 0.15,
    "signal": 0.12,
    "hist": 0.03
  },
  "kdj": {
    "k": 65.5,
    "d": 60.2,
    "j": 75.8
  },
  "rsi": {
    "rsi_6": 58.5,
    "rsi_12": 55.2
  }
}
```

---

### 4. 搜索股票

```http
GET /api/v1/stocks/search
```

**参数:**
- `keyword` (query): 关键词（代码/名称/拼音）

**响应示例:**
```json
[
  {
    "code": "000001",
    "name": "平安银行",
    "price": 15.80,
    "change_percent": 1.28
  }
]
```

---

### 5. 筛选股票

```http
GET /api/v1/stocks/filter
```

**参数:**
- `industry` (query): 行业
- `change_percent_min` (query): 涨跌幅最小值
- `change_percent_max` (query): 涨跌幅最大值
- `volume_min` (query): 最小成交量

---

## 市场数据接口

### 6. 获取大盘指数

```http
GET /api/v1/market/index
```

**响应示例:**
```json
[
  {
    "code": "000001",
    "name": "上证指数",
    "price": 3050.25,
    "change_percent": 0.85
  },
  {
    "code": "399001",
    "name": "深证成指",
    "price": 9850.60,
    "change_percent": 1.20
  }
]
```

---

### 7. 获取涨幅榜

```http
GET /api/v1/market/top-gainers
```

**参数:**
- `limit` (query): 数量，默认 10

---

### 8. 获取跌幅榜

```http
GET /api/v1/market/top-losers
```

**参数:**
- `limit` (query): 数量，默认 10

---

### 9. 获取热门板块

```http
GET /api/v1/market/hot-sectors
```

---

### 10. 获取市场资讯

```http
GET /api/v1/market/news
```

**参数:**
- `keyword` (query): 关键词
- `limit` (query): 数量

---

### 11. 获取行业板块列表

```http
GET /api/v1/market/industries
```

**参数:**
- `page` (query): 页码
- `page_size` (query): 每页数量
- `sort_by` (query): 排序字段

---

## 自选股接口

### 12. 获取自选股列表

```http
GET /api/v1/watchlist
```

---

### 13. 添加自选股

```http
POST /api/v1/watchlist
```

**请求体:**
```json
{
  "stock_code": "000001"
}
```

---

### 14. 删除自选股

```http
DELETE /api/v1/watchlist/{id}
```

---

## 数据源说明

系统支持多数据源智能切换：

| 数据源 | 状态 | 说明 |
|--------|------|------|
| 腾讯财经 | ✅ | 首选数据源，实时行情 |
| AkShare | ✅ | 开源金融数据，涨跌榜 |
| 东方财富 | ✅ | 备用数据源 |
| 新浪财经 | ✅ | 备用数据源 |
| 同花顺 iFinD | 🆕 | HTTP API，需账号 |
| 通达信 | ⚠️ | 部分地区不可用 |
| Tushare | ⚠️ | 需配置 Token |

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 股票未找到 |
| 500 | 服务器错误 |
| 503 | 数据源不可用 |

---

## 使用限制

- 实时行情：每 3 秒可刷新一次
- K 线数据：每日收盘后更新
- 搜索接口：有频率限制，建议缓存结果

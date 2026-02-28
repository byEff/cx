# 📈 A股行情分析系统

一个专业的A股市场行情分析软件，采用前后端分离架构，支持实时行情展示、技术分析、自选股管理等功能。

## 📚 文档导航

- **[README.md](./README.md)** - 项目说明和快速开始（当前文档）
- **[FEATURES.md](./FEATURES.md)** - 功能总结详细文档 ⭐
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - 开发指南和常见问题

## ✨ 核心功能

- ✅ **实时行情展示** - 股票价格、涨跌幅、成交量等实时数据
- ✅ **K线图表分析** - 支持日K/周K/月K，技术指标分析
- ✅ **股票搜索筛选** - 按代码、名称、行业、涨跌幅筛选
- ✅ **自选股管理** - 添加关注股票，价格监控
- ✅ **涨跌排行榜** - 实时涨幅榜、跌幅榜
- ✅ **大盘指数** - 上证指数、深证成指、创业板指
- ✅ **技术指标** - MA、MACD、KDJ、RSI等常用指标
- ✅ **多数据源** - 腾讯财经/AkShare/东方财富/通达信/Tushare 自动切换

## 🛠️ 技术栈

### 后端
- **框架**: Python 3.12 + FastAPI
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **数据源**: 东方财富/新浪财经接口
- **技术分析**: TA-Lib

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5
- **UI组件**: Ant Design 5
- **状态管理**: Zustand
- **HTTP客户端**: Axios

### 部署
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx (生产环境)

## 📦 项目结构

```
cx/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile
│
├── frontend/               # 前端项目
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── services/      # API服务
│   │   └── types/         # 类型定义
│   ├── package.json       # Node依赖
│   └── Dockerfile
│
├── docker-compose.yml      # Docker编排
├── .env.example           # 环境变量模板
└── README.md
```

## 🚀 快速开始

### 前置要求

- Docker Desktop (推荐) 或 Docker + Docker Compose
- Python 3.12+ (本地开发)
- Node.js 20+ (本地开发)

### 使用Docker启动（推荐）

1. **克隆项目**
```bash
cd /Users/zhanggang/code/ai/cx
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，修改必要的配置
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端: http://localhost:5173
- 后端API: http://localhost:8001
- API文档: http://localhost:8001/api/docs

### 本地开发启动

#### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL=postgresql://a_stock:a_stock_2024@localhost:5432/a_stock_db
export REDIS_URL=redis://localhost:6379/0

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📊 API接口文档

### 股票数据接口

```
GET  /api/v1/stocks/realtime          # 获取实时行情
GET  /api/v1/stocks/{code}/quote      # 获取单只股票行情
GET  /api/v1/stocks/{code}/kline      # 获取K线数据
GET  /api/v1/stocks/search            # 搜索股票 (注意：中文关键词需URL编码)
GET  /api/v1/stocks/filter            # 筛选股票
GET  /api/v1/stocks/{code}/analysis   # 获取技术分析
```

**搜索股票示例：**
- 搜索"平安": `GET /api/v1/stocks/search?keyword=%E5%B9%B3%E5%AE%89`
- 搜索"五粮液": `GET /api/v1/stocks/search?keyword=%E4%BA%94%E7%B2%AE%E6%B6%B2`
- 搜索代码: `GET /api/v1/stocks/search?keyword=000001`

### 自选股接口

```
GET  /api/v1/watchlist                # 获取自选股列表
POST /api/v1/watchlist                # 添加自选股
DELETE /api/v1/watchlist/{id}         # 删除自选股
```

### 预警接口

```
GET  /api/v1/alerts                   # 获取预警列表
POST /api/v1/alerts                   # 创建预警
PUT  /api/v1/alerts/{id}/deactivate   # 停用预警
DELETE /api/v1/alerts/{id}            # 删除预警
```

### 市场数据接口

```
GET  /api/v1/market/news              # 获取市场资讯
GET  /api/v1/market/index             # 获取大盘指数
GET  /api/v1/market/top-gainers       # 获取涨幅榜
GET  /api/v1/market/top-losers        # 获取跌幅榜
GET  /api/v1/market/hot-sectors       # 获取热门板块
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL连接URL | postgresql://a_stock:a_stock_2024@postgres:5432/a_stock_db |
| REDIS_URL | Redis连接URL | redis://redis:6379/0 |
| SECRET_KEY | 应用密钥 | - |
| DATA_SOURCE | 数据源类型 | eastmoney |
| ENABLE_ALERTS | 启用预警功能 | true |
| ALERT_CHECK_INTERVAL | 预警检查间隔(秒) | 60 |

### 数据源

系统支持多数据源智能切换，按优先级顺序尝试：

1. **tencent**: 腾讯财经接口（默认首选）
2. **akshare**: AkShare 开源金融数据接口
3. **eastmoney**: 东方财富接口（备用）
4. **tongdaxin**: 通达信接口（备用）
5. **tushare**: Tushare 金融数据接口（需配置Token）

#### Tushare 配置

如需使用 Tushare 数据源，请在 `.env` 文件中配置：

```bash
TUSHARE_TOKEN=your_token_here
```

获取 Token: https://tushare.pro/

## 📱 页面功能

### 首页
- 大盘指数实时展示
- 涨跌排行榜
- 股票搜索

### 股票详情页
- 实时行情数据
- K线数据表格
- 技术指标分析

### 搜索筛选页
- 股票代码/名称搜索（支持中文搜索）
- 按行业、涨跌幅筛选
- 一键添加自选股

### 自选股管理页
- 自选股列表
- 盈亏统计
- 实时价格更新

## ⚠️ 注意事项

### 本地开发说明
- 本地开发使用 SQLite 数据库 (`backend/app/database.db`)
- 前端代理配置已设置，请求 `/api/*` 会转发到后端 `http://localhost:8001`
- 搜索功能支持股票代码和中文名称搜索

### 数据源说明
系统已集成多数据源智能切换功能：
- 腾讯财经 API: 可用 ✅
- AkShare: 可用 ✅
- 东方财富 API: 部分地区不可用
- 通达信 API: 部分地区不可用
- Tushare: 需配置Token

系统会自动按优先级尝试数据源，失败时自动切换到下一个。

## 🔄 数据更新

- **实时行情**: 每3秒自动刷新
- **K线数据**: 每日收盘后更新
- **技术指标**: 实时计算

## 🚧 后续规划

- [ ] 集成TradingView专业图表库
- [ ] WebSocket实时数据推送
- [ ] 价格预警通知（邮件/浏览器通知）
- [ ] 用户系统（注册/登录）
- [ ] 策略回测功能
- [ ] AI预测模型
- [ ] 移动端适配
- [ ] 付费数据源接入

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 数据来源: 腾讯财经、东方财富、通达信
- UI框架: Ant Design
- 图表库: 预留TradingView集成

---

**⚠️ 免责声明**: 本系统仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。

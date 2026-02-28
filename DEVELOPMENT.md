# 快速开发指南

## 本地开发环境设置

### 1. 启动基础服务（PostgreSQL + Redis）

```bash
# 启动PostgreSQL和Redis
docker-compose up -d postgres redis

# 查看服务状态
docker-compose ps
```

### 2. 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL=postgresql://<username>:<password>@localhost:5432/a_stock_db
export REDIS_URL=redis://localhost:6379/0
export SECRET_KEY=<your-secret-key>

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/api/docs

## 常见问题

### 1. TA-Lib安装失败

TA-Lib需要先安装C语言库：

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Ubuntu:**
```bash
sudo apt-get install -y build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### 2. 数据库连接失败

确保PostgreSQL服务正在运行：
```bash
docker-compose ps postgres
```

检查连接字符串是否正确。

### 3. 前端无法连接后端

检查前端代理配置（vite.config.ts）：
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

## 开发工具推荐

### VS Code 扩展

- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- TypeScript Importer
- Auto Rename Tag
- GitLens

### Chrome 扩展

- React Developer Tools
- Redux DevTools

## 代码规范

### Python (后端)

- 使用Black格式化代码
- 使用isort排序import
- 遵循PEP 8规范

```bash
pip install black isort
black app/
isort app/
```

### TypeScript (前端)

- 使用ESLint检查代码
- 使用Prettier格式化代码

```bash
npm run lint
```

## 测试

### 后端测试

```bash
cd backend
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

## 调试技巧

### 后端调试

在代码中添加断点：
```python
import pdb; pdb.set_trace()
```

或使用VS Code调试配置。

### 前端调试

使用浏览器开发者工具和React DevTools。

## 性能优化

### 后端

1. 使用Redis缓存频繁访问的数据
2. 数据库查询优化（添加索引）
3. 异步处理耗时操作

### 前端

1. 使用React.memo避免不必要的重新渲染
2. 使用useMemo和useCallback
3. 代码分割（React.lazy）

## 部署清单

- [ ] 修改SECRET_KEY
- [ ] 关闭DEBUG模式
- [ ] 配置CORS域名
- [ ] 设置数据库备份
- [ ] 配置日志收集
- [ ] 设置监控告警
- [ ] 配置HTTPS证书

## 有用的命令

```bash
# 查看Docker日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 重启服务
docker-compose restart backend
docker-compose restart frontend

# 清理所有容器和数据
docker-compose down -v
```

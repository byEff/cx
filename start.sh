#!/bin/bash

echo "🚀 启动A股行情分析系统..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker Desktop"
    exit 1
fi

# 启动服务
echo "📦 启动Docker容器..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "✅ 服务状态:"
docker-compose ps

echo ""
echo "🎉 启动成功!"
echo "📱 前端地址: http://localhost:5173"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/api/docs"
echo ""
echo "使用 'docker-compose logs -f' 查看日志"
echo "使用 'docker-compose down' 停止服务"

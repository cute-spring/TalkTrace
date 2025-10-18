#!/bin/bash

echo "🚀 设置 Talk Trace 开发环境"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 文件"
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，配置必要的环境变量"
fi

# 创建日志目录
mkdir -p backend/logs

# 构建和启动服务
echo "🔨 构建 Docker 镜像"
docker-compose -f docker-compose.dev.yml build

echo "🚀 启动开发环境"
docker-compose -f docker-compose.dev.yml up -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态"
docker-compose -f docker-compose.dev.yml ps

# 显示访问地址
echo ""
echo "✅ 开发环境启动完成！"
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:8001"
echo "📊 API文档: http://localhost:8001/api"
echo "💚 健康检查: http://localhost:8001/health"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker-compose -f docker-compose.dev.yml logs -f"
echo "  停止服务: docker-compose -f docker-compose.dev.yml down"
echo "  重启服务: docker-compose -f docker-compose.dev.yml restart"
echo ""
echo "🎯 下一步:"
echo "1. 配置 Google Cloud 凭证文件到 backend/credentials/google-credentials.json"
echo "2. 更新 .env 文件中的 GCP_PROJECT_ID"
echo "3. 访问前端应用开始使用"
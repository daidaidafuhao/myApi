#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: Docker Compose未安装${NC}"
    exit 1
fi

# 创建必要的目录
mkdir -p data

# 设置环境变量
if [ ! -f .env ]; then
    echo "TOKEN_SECRET=$(openssl rand -hex 32)" > .env
    echo -e "${GREEN}已创建.env文件${NC}"
fi

# 停止并删除旧容器
echo "停止旧容器..."
docker-compose down

# 构建新镜像
echo "构建新镜像..."
docker-compose build

# 启动服务
echo "启动服务..."
docker-compose up -d

# 检查服务状态
echo "检查服务状态..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}服务已成功启动！${NC}"
    echo "API服务地址: http://localhost:8000"
    echo "API文档地址: http://localhost:8000/docs"
else
    echo -e "${RED}服务启动失败，请检查日志${NC}"
    docker-compose logs
    exit 1
fi 
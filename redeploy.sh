#!/bin/bash

# 设置错误时退出
set -e

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理函数
handle_error() {
    log "错误: $1"
    exit 1
}

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    handle_error "Docker 未运行，请先启动 Docker"
fi

log "开始清理旧容器和镜像..."

# 停止并删除旧容器（如果存在）
if docker ps -a | grep -q myapi; then
    log "停止并删除旧容器 myapi..."
    docker stop myapi || log "停止容器失败，可能已经停止"
    docker rm myapi || log "删除容器失败，可能已经删除"
fi

# 删除旧镜像（如果存在）
if docker images | grep -q myap; then
    log "删除旧镜像 myap..."
    docker rmi myap || log "删除镜像失败，可能已经删除"
fi

log "开始构建新镜像..."
# 构建新镜像
if ! docker build -t myap .; then
    handle_error "镜像构建失败"
fi

log "启动新容器..."
# 运行新容器
if ! docker run -d --name myapi -p 127.0.0.1:8080:8080 myap; then
    handle_error "容器启动失败"
fi

# 等待容器启动
log "等待容器启动..."
sleep 5

# 检查容器是否正在运行
if ! docker ps | grep -q myapi; then
    handle_error "容器启动失败，请检查日志"
fi

log "部署完成！"
log "容器状态："
docker ps | grep myapi

# 显示容器日志
log "容器日志："
docker logs myapi 
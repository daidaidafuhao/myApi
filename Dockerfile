# 使用Python 3.10 slim版本作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY app ./app

# 创建数据目录
RUN mkdir -p /app/data/uploads \
    /app/data/results \
    /app/data/queue

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 初始化数据库
RUN python -m app.init_db

# 设置环境变量
ENV PYTHONPATH=/app \
    PORT=8080

# 暴露端口 (Cloud Run 使用 8080)
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 启动命令
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1 
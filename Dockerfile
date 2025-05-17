# 使用Python 3.10作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 使用国内镜像源（按优先级排序）
# 1. 清华大学镜像源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

# 如果清华镜像不可用，可以取消注释下面的镜像源
# 2. 中科大镜像源
# RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
#     sed -i 's/security.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY app ./app

# 创建数据目录
RUN mkdir -p /app/data/uploads \
    /app/data/results \
    /app/data/queue

# 使用国内PyPI镜像安装Python依赖（按优先级排序）
# 1. 清华大学镜像
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ --no-cache-dir -r requirements.txt

# 如果清华镜像不可用，可以取消注释下面的镜像源
# 2. 中科大镜像
# RUN pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ --no-cache-dir -r requirements.txt

# 初始化数据库
RUN python -m app.init_db

# 设置环境变量
ENV PYTHONPATH=/app
ENV TOKEN_SECRET=your-secret-key-here

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
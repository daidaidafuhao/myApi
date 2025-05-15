# 图像处理 API

这是一个基于 FastAPI 的图像处理 API 服务，提供头像裁剪、人像检测和背景移除等功能。

## 功能特点

- 头像裁剪：自动检测人脸并裁剪成标准尺寸头像
- 人像检测：检测图像中的人物位置
- 背景移除：生成带透明背景的 PNG 图像
- RESTful API 设计
- JWT Token 认证
- Docker 容器化部署
- Redis 缓存支持

## 技术栈

- Python 3.10
- FastAPI
- OpenCV
- MediaPipe
- rembg
- Redis
- Docker

## 快速开始

1. 克隆项目
```bash
git clone <repository-url>
cd <project-directory>
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

3. 使用 Docker Compose 启动服务
```bash
docker-compose up -d
```

4. 访问 API 文档
```
http://localhost:8000/docs
```

## API 接口

### 头像裁剪
- POST `/api/v1/avatar/crop`
- 功能：上传图片并自动裁剪头像
- 需要认证：是

### 人像检测
- POST `/api/v1/person/detect`
- 功能：检测图片中的人物位置
- 需要认证：是

### 背景移除
- POST `/api/v1/background/remove`
- 功能：移除图片背景，生成透明背景图
- 需要认证：是

## 开发说明

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行开发服务器
```bash
uvicorn app.main:app --reload
```

## 部署

项目使用 Docker 进行容器化部署，确保环境一致性：

```bash
docker-compose up -d
```

## 许可证

MIT License 
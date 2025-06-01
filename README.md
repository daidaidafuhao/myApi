# 图像处理 API 服务

这是一个基于 FastAPI 的图像处理服务，提供背景移除、头像裁剪、图片高清化等功能。

## 功能特点

* 背景移除（支持自定义配置）
* 图片高清化（基于AI超分辨率技术）
* 头像裁剪
* 人像检测
* 配置管理（Web界面）
* JWT 认证
* 异步任务队列

## 系统要求

* Python 3.8+
* SQLite3
* 至少 4GB 内存（推荐8GB以上）
* 至少 20GB 磁盘空间（用于AI模型存储）
* CUDA兼容显卡（可选，用于GPU加速）

## 快速开始

### 方式一：直接运行

1. 克隆仓库：
```bash
git clone https://github.com/daidaidafuhao/myApi.git
cd myApi
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
python -m app.init_db
```

4. 启动服务：
```bash
uvicorn app.main:app --reload
```

### 方式二：使用 Docker（推荐）

1. 克隆仓库：
```bash
git clone https://github.com/daidaidafuhao/myApi.git
cd myApi
```

2. 构建 Docker 镜像：
```bash
docker build -t myapi .
```

3. 运行容器：
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  --name myapi \
  myapi
```

注意：
- Docker 构建过程已配置使用国内镜像源，适合国内服务器
- 默认使用清华大学镜像源，如果不可用，可以修改 Dockerfile 使用中科大镜像源
- 使用 `-v` 挂载数据目录和模型目录，确保数据持久化
- 默认端口为 8000，可以通过 `-p` 参数修改

## 访问服务

* API 服务：http://localhost:8000
* API 文档：http://localhost:8000/docs
* 配置管理页面：http://localhost:8000/static/config_list.html

## 目录结构

```
.
├── app/                    # 应用代码
│   ├── core/              # 核心配置
│   ├── models/            # 数据库模型
│   ├── routers/           # API 路由
│   ├── schemas/           # 数据验证
│   ├── static/            # 静态文件
│   └── utils/             # 工具函数
├── data/                  # 运行时数据目录
│   ├── uploads/          # 上传文件
│   ├── results/          # 处理结果
│   └── queue/            # 任务队列
├── models/               # AI模型存储目录
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 构建文件
└── README.md            # 项目文档
```

## 主要功能说明

### 背景移除
- 支持多种模型（u2net等）
- 可自定义处理参数
- 支持 alpha matting
- 异步处理，支持任务状态查询

### 图片高清化 🆕
- 基于Real-ESRGAN等先进AI模型
- 支持2x、4x、8x放大倍数
- 多种模型选择：
  - `RealESRGAN_x4plus`：通用4倍放大模型（推荐）
  - `RealESRNet_x4plus`：4倍放大，更真实纹理
  - `RealESRGAN_x2plus`：2倍放大模型
  - `realesr-animevideov3`：动画/卡通图像专用
- 智能分块处理，支持大图片
- GPU加速支持（可选）
- 异步处理，避免长时间等待

### 配置管理
- Web界面管理配置
- 支持多个配置方案
- 可设置默认配置
- 实时预览效果

### 认证系统
- JWT token认证
- 支持用户登录
- 接口权限控制

## API使用示例

### 图片高清化API

```python
import requests

# 登录获取token
response = requests.post("http://localhost:8000/api/v1/login", params={
    "username": "test_user", 
    "password": "test_password"
})
token = response.json()["access_token"]

# 提交高清化任务
with open("input.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/upscale/enhance",
        files={"file": f},
        params={
            "token": token,
            "scale": 4,
            "model_name": "RealESRGAN_x4plus"
        }
    )
task_id = response.json()["task_id"]

# 查询任务状态
status_response = requests.get(
    f"http://localhost:8000/api/v1/upscale/status/{task_id}",
    params={"token": token}
)

# 下载结果（任务完成后）
result_response = requests.get(
    f"http://localhost:8000/api/v1/upscale/result/{task_id}",
    params={"token": token}
)
with open("enhanced_output.png", "wb") as f:
    f.write(result_response.content)
```

详细API文档请参考：[docs/upscale_api.md](docs/upscale_api.md)

## 测试功能

项目提供了测试脚本来验证图片高清化功能：

```bash
# 测试图片高清化功能
python test_upscale.py [图片路径]
```

如果不提供图片路径，将使用默认测试图片。

## 维护

### 查看日志
```bash
# 直接运行时
# 日志会输出到控制台

# Docker 运行时
docker logs myapi
```

### 重启服务
```bash
# 直接运行时
Ctrl+C
uvicorn app.main:app --reload

# Docker 运行时
docker restart myapi
```

### 数据库维护
```bash
# 直接运行时
python -m app.init_db

# Docker 运行时
docker exec myapi python -m app.init_db
```

### 模型管理
AI模型会在首次使用时自动下载到 `models/` 目录。如需手动清理：

```bash
# 清理下载的模型文件（谨慎操作）
rm -rf models/*

# Docker环境下
docker exec myapi rm -rf models/*
```

## 性能优化

### GPU加速
如果有NVIDIA GPU，安装CUDA版本的PyTorch可以显著提升图片高清化速度：

```bash
# 卸载CPU版本
pip uninstall torch torchvision

# 安装CUDA版本（根据你的CUDA版本选择）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 内存优化
- 调整 `tile_size` 参数：内存充足时增大，内存不足时减小
- 启用 `half_precision` 可减少内存使用并提升速度
- 对于大图片，系统会自动进行分块处理

## 安全建议

1. 在生产环境中修改默认的 `TOKEN_SECRET`
2. 配置适当的防火墙规则
3. 使用 HTTPS
4. 定期备份数据库
5. 监控系统资源使用情况
6. 限制上传文件大小，避免服务器资源耗尽

## 许可证

MIT 
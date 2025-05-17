# 图像处理 API 服务

这是一个基于 FastAPI 的图像处理服务，提供背景移除、头像裁剪等功能。

## 功能特点

- 背景移除
- 头像裁剪
- 人像检测
- 配置管理
- JWT 认证
- Redis 缓存

## 系统要求

- Docker
- Docker Compose
- 至少 2GB 内存
- 至少 10GB 磁盘空间

## 快速部署

1. 克隆仓库：
```bash
git clone <repository-url>
cd <repository-name>
```

2. 运行部署脚本：
```bash
chmod +x deploy.sh
./deploy.sh
```

部署脚本会自动：
- 检查必要的依赖
- 创建必要的目录
- 生成安全的密钥
- 构建并启动服务

## 手动部署

1. 创建环境变量文件：
```bash
echo "TOKEN_SECRET=$(openssl rand -hex 32)" > .env
```

2. 构建并启动服务：
```bash
docker-compose up -d
```

## 访问服务

- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 配置管理页面：http://localhost:8000/static/config_list.html

## 环境变量

- `TOKEN_SECRET`: JWT 令牌密钥
- `REDIS_HOST`: Redis 服务器地址
- `REDIS_PORT`: Redis 服务器端口
- `MAX_UPLOAD_SIZE`: 最大上传文件大小（字节）

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
├── data/                  # 数据目录
├── Dockerfile            # Docker 配置
├── docker-compose.yml    # Docker Compose 配置
├── deploy.sh             # 部署脚本
└── requirements.txt      # Python 依赖
```

## 维护

### 查看日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 停止服务
```bash
docker-compose down
```

### 更新服务
```bash
git pull
./deploy.sh
```

## 故障排除

1. 如果服务无法启动，检查日志：
```bash
docker-compose logs
```

2. 如果数据库出现问题，可以重新初始化：
```bash
docker-compose exec api python -m app.init_db
```

3. 如果 Redis 出现问题，可以重置数据：
```bash
docker-compose down -v
docker-compose up -d
```

## 安全建议

1. 在生产环境中修改默认的 `TOKEN_SECRET`
2. 配置适当的防火墙规则
3. 使用 HTTPS
4. 定期备份数据
5. 监控系统资源使用情况

## 许可证

MIT 
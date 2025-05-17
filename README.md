# 图像处理 API 服务

这是一个基于 FastAPI 的图像处理服务，提供背景移除、头像裁剪等功能。

## 功能特点

* 背景移除（支持自定义配置）
* 头像裁剪
* 人像检测
* 配置管理（Web界面）
* JWT 认证
* 异步任务队列

## 系统要求

* Python 3.8+
* SQLite3
* 至少 2GB 内存
* 至少 10GB 磁盘空间

## 快速开始

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
├── requirements.txt      # Python 依赖
└── README.md            # 项目文档
```

## 主要功能说明

### 背景移除
- 支持多种模型（u2net等）
- 可自定义处理参数
- 支持 alpha matting
- 异步处理，支持任务状态查询

### 配置管理
- Web界面管理配置
- 支持多个配置方案
- 可设置默认配置
- 实时预览效果

### 认证系统
- JWT token认证
- 支持用户登录
- 接口权限控制

## 维护

### 查看日志
服务启动时会输出日志到控制台

### 重启服务
```bash
# 停止服务
Ctrl+C

# 重新启动
uvicorn app.main:app --reload
```

### 数据库维护
```bash
# 重新初始化数据库
python -m app.init_db
```

## 安全建议

1. 在生产环境中修改默认的 `TOKEN_SECRET`
2. 配置适当的防火墙规则
3. 使用 HTTPS
4. 定期备份数据库
5. 监控系统资源使用情况

## 许可证

MIT 
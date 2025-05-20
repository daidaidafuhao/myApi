import os
import multiprocessing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from jose import jwt
from .core.config import settings
from .routers import background, avatar, person, config
from app.worker import start_worker
from fastapi.responses import FileResponse

# 设置环境变量以解决OpenMP线程冲突问题
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'  # 限制OpenMP线程数为1

# 确保在Windows上使用spawn方式启动进程
multiprocessing.set_start_method('spawn', force=True) if __name__ == '__main__' else None

# 创建 FastAPI 应用实例
# 设置应用标题、描述和版本信息
app = FastAPI(
    title="Image Processing API",
    description="API for image processing tasks including background removal, avatar cropping, and person detection",
    version="1.0.0"
)

# 配置 CORS（跨源资源共享）中间件
# 允许所有来源的请求，支持凭证，允许所有方法和头部
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 注册路由到应用
# 为每个路由添加前缀和标签，便于 API 文档分类
app.include_router(background.router, prefix="/api/v1/background", tags=["background"])
app.include_router(avatar.router, prefix="/api/v1/avatar", tags=["avatar"])
app.include_router(person.router, prefix="/api/v1/person", tags=["person"])
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])

# 根路由重定向到配置列表页面
@app.get("/")
async def root():
    return FileResponse("app/static/index.html")

# 登录路由，用于获取访问令牌
@app.post("/api/v1/login", tags=["Authentication"])
async def login(username: str = "test_user", password: str = "test_password"):
    """
    登录接口，用于获取访问令牌
    
    参数:
        username: 用户名
        password: 密码
    
    返回:
        dict: 包含访问令牌的字典
    """
    # 这里简化了验证过程，实际应用中应该验证用户名和密码
    if username == "test_user" and password == "test_password":
        # 创建令牌数据
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "exp": expire,
            "sub": username
        }
        # 生成令牌
        access_token = jwt.encode(to_encode, settings.TOKEN_SECRET, algorithm="HS256")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    return {"error": "Invalid credentials"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def start_worker_process():
    """启动工作进程"""
    # 确保工作进程使用spawn方式启动，避免OpenMP线程冲突
    ctx = multiprocessing.get_context('spawn')
    worker_process = ctx.Process(target=start_worker)
    worker_process.start()
    return worker_process

@app.on_event("startup")
async def startup_event():
    """应用启动时的事件处理"""
    # 创建必要的目录
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/results/images", exist_ok=True)
    os.makedirs("data/queue", exist_ok=True)
    
    # 输出环境变量设置，确认OpenMP线程冲突解决方案已生效
    print("API服务启动，环境变量已配置以避免OpenMP线程冲突")
    print(f"KMP_DUPLICATE_LIB_OK: {os.environ.get('KMP_DUPLICATE_LIB_OK')}")
    print(f"OMP_NUM_THREADS: {os.environ.get('OMP_NUM_THREADS')}")
    
    # 确保环境变量设置正确
    print(f"OpenMP环境变量设置：")
    print(f"KMP_DUPLICATE_LIB_OK: {os.environ.get('KMP_DUPLICATE_LIB_OK')}")
    print(f"OMP_NUM_THREADS: {os.environ.get('OMP_NUM_THREADS')}")
    print(f"多进程启动方式: {multiprocessing.get_start_method()}")

    # 启动工作进程
    app.state.worker_process = start_worker_process()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的事件处理"""
    # 停止工作进程
    if hasattr(app.state, "worker_process"):
        app.state.worker_process.terminate()
        app.state.worker_process.join()
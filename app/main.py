from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from jose import jwt
from .core.config import settings
from .routers import background, avatar, person, config

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
app.include_router(background.router, prefix="/background", tags=["background"])
app.include_router(avatar.router, prefix="/avatar", tags=["avatar"])
app.include_router(person.router, prefix="/person", tags=["person"])
app.include_router(config.router, prefix="/config", tags=["config"])

# 根路由重定向到配置列表页面
@app.get("/")
async def root():
    return {"message": "Welcome to Image Processing API", "config_page": "/static/config_list.html"}

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
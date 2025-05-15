from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    应用配置类
    使用 pydantic 的 BaseSettings 进行配置管理
    支持从环境变量和 .env 文件加载配置
    """
    
    # API 相关配置
    API_V1_STR: str = "/api/v1"  # API 版本前缀
    PROJECT_NAME: str = "Image Processing API"  # 项目名称
    
    # 安全相关配置
    TOKEN_SECRET: str  # JWT 令牌密钥，必须从环境变量设置
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 访问令牌过期时间（分钟）
    
    # 文件上传相关配置
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 最大上传文件大小（5MB）
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png"}  # 允许的图片格式
    
    # Redis 缓存配置
    REDIS_HOST: str = "redis"  # Redis 服务器地址
    REDIS_PORT: int = 6379  # Redis 服务器端口
    
    class Config:
        env_file = ".env"  # 指定环境变量文件路径

# 创建全局配置实例
settings = Settings() 
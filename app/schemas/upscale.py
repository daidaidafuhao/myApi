from pydantic import BaseModel
from typing import Optional

class UpscaleResponse(BaseModel):
    """图片处理响应模型"""
    task_id: str
    message: str

class EnhanceResponse(BaseModel):
    """图片高清化响应模型"""
    task_id: str
    message: str

class ComboResponse(BaseModel):
    """背景移除+高清化组合响应模型"""
    task_id: str
    message: str

class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: str  # pending, processing, completed, failed
    result_path: Optional[str] = None
    error: Optional[str] = None

class EnhanceConfig(BaseModel):
    """图片高清化配置"""
    enhance_level: str = "medium"  # light, medium, strong

class UpscaleConfig(BaseModel):
    """图片放大配置"""
    scale: int = 4  # 2, 4, 8
    method: str = "lanczos"  # lanczos, cubic, linear
    enhance_quality: bool = True

class ComboConfig(BaseModel):
    """背景移除+高清化组合配置"""
    enhance_level: str = "medium"  # light, medium, strong
    config_id: Optional[int] = None  # 背景移除配置ID，None使用默认配置 
from pydantic import BaseModel, Field
from typing import Optional

class BackgroundRemovalConfigBase(BaseModel):
    """背景移除配置基础模型"""
    name: str = Field(..., description="配置名称")
    model: str = Field(default="u2net", description="使用的模型")
    max_size: int = Field(default=800, description="最大处理尺寸")
    use_alpha_matting: bool = Field(default=True, description="是否使用alpha matting")
    alpha_foreground: int = Field(default=240, description="alpha matting前景阈值")
    alpha_background: int = Field(default=10, description="alpha matting背景阈值")
    alpha_erode: int = Field(default=15, description="alpha matting腐蚀尺寸")
    is_default: bool = Field(default=False, description="是否为默认配置")
    description: Optional[str] = Field(None, description="配置描述")

class BackgroundRemovalConfigCreate(BackgroundRemovalConfigBase):
    """创建背景移除配置的请求模型"""
    pass

class BackgroundRemovalConfigUpdate(BaseModel):
    """更新背景移除配置的请求模型"""
    name: Optional[str] = Field(None, description="配置名称")
    model: Optional[str] = Field(None, description="使用的模型")
    max_size: Optional[int] = Field(None, description="最大处理尺寸")
    use_alpha_matting: Optional[bool] = Field(None, description="是否使用alpha matting")
    alpha_foreground: Optional[int] = Field(None, description="alpha matting前景阈值")
    alpha_background: Optional[int] = Field(None, description="alpha matting背景阈值")
    alpha_erode: Optional[int] = Field(None, description="alpha matting腐蚀尺寸")
    is_default: Optional[bool] = Field(None, description="是否为默认配置")
    description: Optional[str] = Field(None, description="配置描述")

class BackgroundRemovalConfigResponse(BackgroundRemovalConfigBase):
    """背景移除配置的响应模型"""
    id: int = Field(..., description="配置ID")

    class Config:
        orm_mode = True 
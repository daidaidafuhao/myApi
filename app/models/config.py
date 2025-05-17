from sqlalchemy import Column, Integer, String, Boolean, JSON
from ..database import Base

class BackgroundRemovalConfig(Base):
    """背景移除配置模型"""
    __tablename__ = "background_removal_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, comment="配置名称")
    model = Column(String(50), default="u2net", comment="使用的模型")
    max_size = Column(Integer, default=800, comment="最大处理尺寸")
    use_alpha_matting = Column(Boolean, default=True, comment="是否使用alpha matting")
    alpha_foreground = Column(Integer, default=240, comment="alpha matting前景阈值")
    alpha_background = Column(Integer, default=10, comment="alpha matting背景阈值")
    alpha_erode = Column(Integer, default=15, comment="alpha matting腐蚀尺寸")
    is_default = Column(Boolean, default=False, comment="是否为默认配置")
    description = Column(String(200), nullable=True, comment="配置描述") 
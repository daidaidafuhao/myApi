from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
import cv2
import numpy as np
from PIL import Image
import io
from sqlalchemy.orm import Session
from ..utils.image_processing import validate_image
from ..utils.image_utils import change_background
from ..core.security import verify_token
from ..database import get_db
from ..models.config import BackgroundRemovalConfig

# 创建路由实例
router = APIRouter()

async def get_current_user(token: str = Depends(verify_token)):
    """
    验证用户令牌的依赖函数
    
    参数:
        token (str): JWT 令牌
    
    返回:
        dict: 解码后的令牌数据
    
    异常:
        HTTPException: 当令牌无效时抛出 401 错误
    """
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return token

@router.post("/remove")
async def remove_background_endpoint(
    image: UploadFile = File(...),
    config_id: int = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    背景移除接口
    
    参数:
        image (UploadFile): 上传的图片文件
        config_id (int, optional): 配置ID，如果不指定则使用默认配置
        current_user (dict): 当前用户信息（通过令牌验证）
        db (Session): 数据库会话
    
    返回:
        Response: 包含处理后的图片数据的响应
        返回带有透明背景的 PNG 图像
    """
    # 验证图片
    if not validate_image(image):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    try:
        # 获取配置
        if config_id:
            config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.id == config_id).first()
            if not config:
                raise HTTPException(status_code=404, detail="Configuration not found")
        else:
            config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.is_default == True).first()
            if not config:
                raise HTTPException(status_code=404, detail="No default configuration found")
        
        # 读取图片内容
        contents = await image.read()
        
        # 将图片内容转换为PIL Image对象
        input_image = Image.open(io.BytesIO(contents))
        
        # 创建内存中的输出流
        output_buffer = io.BytesIO()
        
        # 使用image_utils处理图片
        change_background(
            input_image=input_image,
            output_path=output_buffer,
            bg_color=(0, 0, 0, 0),  # 透明背景
            max_size=config.max_size,
            model=config.model,
            use_alpha_matting=config.use_alpha_matting,
            alpha_foreground=config.alpha_foreground,
            alpha_background=config.alpha_background,
            alpha_erode=config.alpha_erode
        )
        
        # 获取处理后的图片数据
        output_buffer.seek(0)
        processed_image = output_buffer.getvalue()
        
        # 返回处理后的图片
        return Response(
            content=processed_image,
            media_type="image/png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理图片时出错: {str(e)}") 
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
import cv2
import numpy as np
from PIL import Image
import io
from ..utils.image_processing import validate_image
from ..utils.image_utils import change_background
from ..core.security import verify_token

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
    current_user: dict = Depends(get_current_user)
):
    """
    背景移除接口
    
    参数:
        image (UploadFile): 上传的图片文件
        current_user (dict): 当前用户信息（通过令牌验证）
    
    返回:
        Response: 包含处理后的图片数据的响应
        返回带有透明背景的 PNG 图像
    
    处理流程:
        1. 验证上传的图片文件
        2. 读取图片数据
        3. 使用 image_utils 移除背景
        4. 返回处理后的图片
    """
    # 验证图片
    if not validate_image(image):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    try:
        # 读取图片内容
        contents = await image.read()
        
        # 将图片内容转换为PIL Image对象
        input_image = Image.open(io.BytesIO(contents))
        
        # 创建内存中的输出流
        output_buffer = io.BytesIO()
        
        # 使用image_utils处理图片
        # 设置透明背景 (0,0,0,0)
        change_background(
            input_image=input_image,
            output_path=output_buffer,
            bg_color=(0, 0, 0, 0),  # 透明背景
            max_size=800,  # 最大处理尺寸
            model="u2net",  # 使用u2net模型
            use_alpha_matting=True,  # 使用alpha matting获得更好的边缘效果
            alpha_foreground=240,
            alpha_background=10,
            alpha_erode=20
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
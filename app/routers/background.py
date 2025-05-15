from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
import cv2
import numpy as np
from ..utils.image_processing import validate_image, remove_background
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
        3. 移除背景
        4. 转换为 PNG 格式
        5. 返回处理后的图片
    """
    # 验证图片
    if not validate_image(image):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 读取图片
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 移除背景
    result = remove_background(img)
    
    # 转换为PNG格式
    _, png = cv2.imencode('.png', result)
    
    # 返回结果
    return Response(
        content=png.tobytes(),
        media_type="image/png"
    ) 
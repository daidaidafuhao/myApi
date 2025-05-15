from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from ..utils.image_processing import validate_image, detect_faces, crop_avatar
from ..core.security import verify_token
from typing import Optional

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

@router.post("/crop")
async def crop_avatar_endpoint(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    头像裁剪接口
    
    参数:
        image (UploadFile): 上传的图片文件
        current_user (dict): 当前用户信息（通过令牌验证）
    
    返回:
        JSONResponse: 包含处理结果的 JSON 响应
    
    处理流程:
        1. 验证上传的图片文件
        2. 读取图片数据
        3. 检测人脸位置
        4. 裁剪头像
        5. 返回处理结果
    """
    # 验证图片
    if not validate_image(image):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 读取图片
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 检测人脸
    faces = detect_faces(img)
    if not faces:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    # 裁剪头像
    avatar = crop_avatar(img, faces[0])
    
    # 返回结果
    return JSONResponse(
        content={
            "status": "success",
            "message": "Avatar cropped successfully",
            "face_count": len(faces)
        }
    ) 
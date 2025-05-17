from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import Response, FileResponse
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
from typing import Optional
import os
from pathlib import Path

from app.utils.task_queue import TaskQueue
from app.schemas.background_removal import BackgroundRemovalResponse, TaskStatusResponse

# 创建路由实例
router = APIRouter()
task_queue = TaskQueue()

async def get_current_user(token: str = Query(..., description="JWT token")):
    """
    验证用户令牌的依赖函数
    
    参数:
        token (str): JWT 令牌（从URL参数获取）
    
    返回:
        dict: 解码后的令牌数据
    
    异常:
        HTTPException: 当令牌无效时抛出 401 错误
    """
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return verify_token(token)

@router.post("/remove", response_model=BackgroundRemovalResponse)
async def remove_background(
    token: str = Query(..., description="JWT token"),
    file: UploadFile = File(..., description="Image file to process"),
    config_id: Optional[int] = Query(None, description="Configuration ID"),
    db: Session = Depends(get_db)
):
    """提交背景移除任务"""
    # 验证用户
    current_user = await get_current_user(token)
    
    # 验证图片
    if not validate_image(file):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 获取配置
    if config_id:
        config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.id == config_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
    else:
        config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.is_default == True).first()
        if not config:
            raise HTTPException(status_code=404, detail="No default configuration found")
    
    # 创建上传目录
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存上传的文件
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 添加到任务队列
    task_id = task_queue.add_task(
        task_type="background_removal",
        params={
            "input_path": str(file_path),
            "user_id": current_user.get("sub"),
            "config": {
                "max_size": config.max_size,
                "model": config.model,
                "use_alpha_matting": config.use_alpha_matting,
                "alpha_foreground": config.alpha_foreground,
                "alpha_background": config.alpha_background,
                "alpha_erode": config.alpha_erode
            }
        }
    )
    
    return BackgroundRemovalResponse(
        task_id=task_id,
        message="Task submitted successfully"
    )

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取任务状态"""
    task_data = task_queue.get_task_status(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 检查用户权限
    if task_data['params'].get('user_id') != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task_data['status'],
        result_path=task_data.get('result_path'),
        error=task_data.get('error')
    )

@router.get("/result/{task_id}")
async def get_task_result(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """获取任务结果"""
    task_data = task_queue.get_task_status(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 检查用户权限
    if task_data['params'].get('user_id') != current_user.get("sub"):
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    # 检查任务状态
    if task_data['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Task not completed")
    
    # 返回结果文件
    result_path = task_data.get('result_path')
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        result_path,
        media_type="image/png",
        filename=f"result_{task_id}.png"
    ) 
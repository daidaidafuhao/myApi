from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..utils.image_processing import validate_image
from ..core.security import verify_token
from ..database import get_db
from typing import Optional
import os
from pathlib import Path

from app.utils.task_queue import TaskQueue
from app.schemas.upscale import UpscaleResponse, EnhanceResponse, ComboResponse, TaskStatusResponse

# 创建路由实例
router = APIRouter()
task_queue = TaskQueue()

def _check_upscale_availability():
    """检查图片高清化功能是否可用"""
    try:
        from app.utils.simple_upscale import get_simple_upscale_processor
        return True
    except ImportError as e:
        return False, str(e)

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

@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_image(
    token: str = Query(..., description="JWT token"),
    file: UploadFile = File(..., description="Image file to enhance"),
    enhance_level: str = Query("medium", description="Enhancement level (light, medium, strong)"),
    db: Session = Depends(get_db)
):
    """提交图片高清化任务（保持原尺寸，提升质量）"""
    # 验证用户
    current_user = await get_current_user(token)
    
    # 检查功能可用性
    availability = _check_upscale_availability()
    if availability is not True:
        raise HTTPException(
            status_code=503, 
            detail=f"图片高清化功能暂时不可用。错误: {availability[1] if isinstance(availability, tuple) else '未知错误'}"
        )
    
    # 验证图片
    if not validate_image(file):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 验证参数
    if enhance_level.lower() not in ["light", "medium", "strong"]:
        raise HTTPException(status_code=400, detail="Enhancement level must be light, medium, or strong")
    
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
        task_type="enhance",
        params={
            "input_path": str(file_path),
            "user_id": current_user.get("sub"),
            "config": {
                "enhance_level": enhance_level
            }
        }
    )
    
    return EnhanceResponse(
        task_id=task_id,
        message="Image enhancement task submitted successfully (same size, improved quality)"
    )

@router.post("/upscale", response_model=UpscaleResponse)
async def upscale_image(
    token: str = Query(..., description="JWT token"),
    file: UploadFile = File(..., description="Image file to upscale"),
    scale: int = Query(4, description="Upscale factor (2, 4, 8)"),
    method: str = Query("lanczos", description="Interpolation method (lanczos, cubic, linear)"),
    enhance_quality: bool = Query(True, description="Apply quality enhancement"),
    db: Session = Depends(get_db)
):
    """提交图片放大任务（改变尺寸）"""
    # 验证用户
    current_user = await get_current_user(token)
    
    # 检查功能可用性
    availability = _check_upscale_availability()
    if availability is not True:
        raise HTTPException(
            status_code=503, 
            detail=f"图片放大功能暂时不可用。错误: {availability[1] if isinstance(availability, tuple) else '未知错误'}"
        )
    
    # 验证图片
    if not validate_image(file):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 验证参数
    if scale not in [2, 4, 8]:
        raise HTTPException(status_code=400, detail="Scale must be 2, 4, or 8")
    
    if method.lower() not in ["lanczos", "cubic", "linear"]:
        raise HTTPException(status_code=400, detail="Method must be lanczos, cubic, or linear")
    
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
        task_type="upscale",
        params={
            "input_path": str(file_path),
            "user_id": current_user.get("sub"),
            "config": {
                "scale": scale,
                "method": method,
                "enhance_quality": enhance_quality
            }
        }
    )
    
    return UpscaleResponse(
        task_id=task_id,
        message="Image upscale task submitted successfully (size will be changed)"
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
        filename=f"enhanced_{task_id}.png"
    )

@router.post("/combo", response_model=ComboResponse)
async def combo_bg_remove_and_enhance(
    token: str = Query(..., description="JWT token"),
    file: UploadFile = File(..., description="Image file to process"),
    enhance_level: str = Query("medium", description="Enhancement level (light, medium, strong)"),
    config_id: Optional[int] = Query(None, description="Background removal configuration ID"),
    db: Session = Depends(get_db)
):
    """提交背景移除+高清化组合任务"""
    # 验证用户
    current_user = await get_current_user(token)
    
    # 检查功能可用性
    availability = _check_upscale_availability()
    if availability is not True:
        raise HTTPException(
            status_code=503, 
            detail=f"图片高清化功能暂时不可用。错误: {availability[1] if isinstance(availability, tuple) else '未知错误'}"
        )
    
    # 验证图片
    if not validate_image(file):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 验证参数
    if enhance_level.lower() not in ["light", "medium", "strong"]:
        raise HTTPException(status_code=400, detail="Enhancement level must be light, medium, or strong")
    
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
        task_type="combo_bg_enhance",
        params={
            "input_path": str(file_path),
            "user_id": current_user.get("sub"),
            "config": {
                "enhance_level": enhance_level,
                "config_id": config_id
            }
        }
    )
    
    return ComboResponse(
        task_id=task_id,
        message="Background removal + enhancement combo task submitted successfully"
    ) 
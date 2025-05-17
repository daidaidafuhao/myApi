from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from typing import Optional
import os
from pathlib import Path

from app.core.auth import get_current_user
from app.utils.task_queue import TaskQueue
from app.schemas.background_removal import BackgroundRemovalResponse, TaskStatusResponse

router = APIRouter()
task_queue = TaskQueue()

@router.post("/remove", response_model=BackgroundRemovalResponse)
async def remove_background(
    file: UploadFile = File(...),
    config_id: Optional[int] = Query(None, description="背景移除配置ID，不提供则使用默认配置"),
    current_user = Depends(get_current_user)
):
    """提交背景移除任务"""
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
            "user_id": current_user.id,
            "config_id": config_id
        }
    )
    
    return BackgroundRemovalResponse(
        task_id=task_id,
        message="Task submitted successfully"
    )

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user = Depends(get_current_user)
):
    """获取任务状态"""
    task_data = task_queue.get_task_status(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 检查用户权限
    if task_data['params'].get('user_id') != current_user.id:
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
    current_user = Depends(get_current_user)
):
    """获取任务结果"""
    task_data = task_queue.get_task_status(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 检查用户权限
    if task_data['params'].get('user_id') != current_user.id:
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
import os
import time
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from app.utils.task_queue import TaskQueue
from app.utils.image_utils import change_background
from app.core.config import settings
from app.database import SessionLocal
from app.models.config import BackgroundRemovalConfig

class Worker:
    def __init__(self):
        self.task_queue = TaskQueue()
        self.running = False
    
    def start(self):
        """启动工作进程"""
        self.running = True
        print("Worker started...")
        
        while self.running:
            try:
                # 获取下一个任务
                task = self.task_queue.get_next_task()
                if not task:
                    time.sleep(1)  # 没有任务时等待1秒
                    continue
                
                task_id, task_data = task
                print(f"Processing task {task_id}...")
                
                try:
                    # 处理任务
                    result_path = self._process_task(task_data)
                    # 完成任务
                    self.task_queue.complete_task(task_id, result_path=result_path)
                except Exception as e:
                    print(f"Error processing task {task_id}: {str(e)}")
                    self.task_queue.complete_task(task_id, error=str(e))
                
            except Exception as e:
                print(f"Worker error: {str(e)}")
                time.sleep(1)
    
    def stop(self):
        """停止工作进程"""
        self.running = False
    
    def _process_task(self, task_data: dict) -> Optional[str]:
        """处理单个任务"""
        task_type = task_data['type']
        params = task_data['params']
        
        # 创建结果目录
        result_dir = Path("data/results/images")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # 处理不同类型的任务
        if task_type == "background_removal":
            # 获取输入图片路径
            input_path = params.get('input_path')
            if not input_path or not os.path.exists(input_path):
                raise ValueError("Input image not found")
            
            # 生成输出路径
            output_path = result_dir / f"{task_data['id']}.png"
            
            # 获取配置
            db = SessionLocal()
            try:
                config_id = params.get('config_id')
                if config_id:
                    config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.id == config_id).first()
                    if not config:
                        raise ValueError(f"Configuration {config_id} not found")
                else:
                    config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.is_default == True).first()
                    if not config:
                        raise ValueError("No default configuration found")
                
                # 处理图片
                change_background(
                    input_image=input_path,
                    output_path=str(output_path),
                    model=config.model,
                    use_alpha_matting=config.use_alpha_matting,
                    alpha_foreground=config.alpha_foreground,
                    alpha_background=config.alpha_background,
                    alpha_erode=config.alpha_erode
                )
                
                return str(output_path)
            finally:
                db.close()
        
        raise ValueError(f"Unknown task type: {task_type}")

def start_worker():
    """启动工作进程"""
    worker = Worker()
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()
        print("Worker stopped.") 
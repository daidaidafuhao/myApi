import os
import json
import time
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class TaskQueue:
    def __init__(self, queue_dir: str = "data/queue", result_dir: str = "data/results"):
        self.queue_dir = Path(queue_dir)
        self.result_dir = Path(result_dir)
        self.processing_dir = self.queue_dir / "processing"
        
        # 创建必要的目录
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.processing_dir.mkdir(parents=True, exist_ok=True)
        
        # 清理过期的结果
        self._cleanup_expired_results()
    
    def _cleanup_expired_results(self):
        """清理过期的结果文件"""
        now = datetime.now()
        for result_file in self.result_dir.glob("*.json"):
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    created_at = datetime.fromisoformat(data['created_at'])
                    if now - created_at > timedelta(hours=1):
                        # 删除结果文件和相关的图片文件
                        result_file.unlink()
                        if 'result_path' in data:
                            result_image = Path(data['result_path'])
                            if result_image.exists():
                                result_image.unlink()
            except Exception:
                # 如果文件损坏，直接删除
                result_file.unlink()
    
    def add_task(self, task_type: str, params: Dict) -> str:
        """添加新任务到队列"""
        task_id = str(uuid.uuid4())
        task_file = self.queue_dir / f"{task_id}.json"
        
        task_data = {
            'id': task_id,
            'type': task_type,
            'params': params,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        with open(task_file, 'w') as f:
            json.dump(task_data, f)
        
        return task_id
    
    def get_next_task(self) -> Optional[Tuple[str, Dict]]:
        """获取下一个待处理的任务"""
        # 获取所有待处理的任务
        pending_tasks = list(self.queue_dir.glob("*.json"))
        if not pending_tasks:
            return None
        
        # 按创建时间排序
        pending_tasks.sort(key=lambda x: x.stat().st_mtime)
        task_file = pending_tasks[0]
        
        try:
            with open(task_file, 'r') as f:
                task_data = json.load(f)
            
            # 移动任务到处理中目录
            processing_file = self.processing_dir / task_file.name
            shutil.move(str(task_file), str(processing_file))
            
            return task_data['id'], task_data
        except Exception:
            # 如果文件损坏，直接删除
            task_file.unlink()
            return None
    
    def complete_task(self, task_id: str, result_path: Optional[str] = None, error: Optional[str] = None):
        """完成任务并保存结果"""
        processing_file = self.processing_dir / f"{task_id}.json"
        if not processing_file.exists():
            return
        
        try:
            with open(processing_file, 'r') as f:
                task_data = json.load(f)
            
            # 更新任务状态
            task_data['status'] = 'completed' if not error else 'failed'
            task_data['completed_at'] = datetime.now().isoformat()
            if result_path:
                task_data['result_path'] = result_path
            if error:
                task_data['error'] = error
            
            # 保存结果
            result_file = self.result_dir / f"{task_id}.json"
            with open(result_file, 'w') as f:
                json.dump(task_data, f)
            
            # 删除处理中的文件
            processing_file.unlink()
        except Exception:
            # 如果出错，确保清理文件
            processing_file.unlink()
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        # 检查处理中的任务
        processing_file = self.processing_dir / f"{task_id}.json"
        if processing_file.exists():
            with open(processing_file, 'r') as f:
                task_data = json.load(f)
            task_data['status'] = 'processing'
            return task_data
        
        # 检查已完成的任务
        result_file = self.result_dir / f"{task_id}.json"
        if result_file.exists():
            with open(result_file, 'r') as f:
                return json.load(f)
        
        # 检查队列中的任务
        queue_file = self.queue_dir / f"{task_id}.json"
        if queue_file.exists():
            with open(queue_file, 'r') as f:
                return json.load(f)
        
        return None 
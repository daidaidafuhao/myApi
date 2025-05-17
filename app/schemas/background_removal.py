from pydantic import BaseModel
from typing import Optional

class BackgroundRemovalResponse(BaseModel):
    task_id: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result_path: Optional[str] = None
    error: Optional[str] = None 
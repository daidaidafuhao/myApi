from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.config import BackgroundRemovalConfig
from ..schemas.config import (
    BackgroundRemovalConfigCreate,
    BackgroundRemovalConfigUpdate,
    BackgroundRemovalConfigResponse
)
from ..core.security import verify_token

router = APIRouter()

async def get_current_user(authorization: str = Header(...)):
    """验证用户令牌"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    token = authorization.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return payload

@router.get("/background-configs", response_model=List[BackgroundRemovalConfigResponse])
async def get_background_configs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取所有背景移除配置"""
    configs = db.query(BackgroundRemovalConfig).all()
    return configs

@router.get("/background-configs/{config_id}", response_model=BackgroundRemovalConfigResponse)
async def get_background_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取特定背景移除配置"""
    config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.post("/background-configs", response_model=BackgroundRemovalConfigResponse)
async def create_background_config(
    config: BackgroundRemovalConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建新的背景移除配置"""
    # 如果设置为默认配置，需要将其他配置的默认状态设为False
    if config.is_default:
        db.query(BackgroundRemovalConfig).update({"is_default": False})
    
    db_config = BackgroundRemovalConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.put("/background-configs/{config_id}", response_model=BackgroundRemovalConfigResponse)
async def update_background_config(
    config_id: int,
    config: BackgroundRemovalConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新背景移除配置"""
    db_config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # 如果设置为默认配置，需要将其他配置的默认状态设为False
    if config.is_default:
        db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.id != config_id).update({"is_default": False})
    
    for key, value in config.dict(exclude_unset=True).items():
        setattr(db_config, key, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config

@router.delete("/background-configs/{config_id}")
async def delete_background_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """删除背景移除配置"""
    db_config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if db_config.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default configuration")
    
    db.delete(db_config)
    db.commit()
    return {"message": "Configuration deleted successfully"} 
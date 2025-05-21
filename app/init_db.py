from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.config import BackgroundRemovalConfig
from app.database import Base

def init_db():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有默认配置
        default_config = db.query(BackgroundRemovalConfig).filter(BackgroundRemovalConfig.is_default == True).first()
        if not default_config:
            # 创建默认配置
            default_config = BackgroundRemovalConfig(
                name="默认配置",
                model="u2netp",
                max_size=800,
                use_alpha_matting=True,
                alpha_foreground=240,
                alpha_background=10,
                alpha_erode=20,
                is_default=True,
                description="默认的背景移除配置"
            )
            db.add(default_config)
            db.commit()
            print("已创建默认配置")
    except Exception as e:
        print(f"初始化数据库时出错: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 
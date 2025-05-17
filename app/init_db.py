from app.database import engine
from app.models.config import Base

def init_db():
    # 创建所有表
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!") 
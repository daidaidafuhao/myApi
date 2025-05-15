from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from .config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌
    
    参数:
        data (dict): 要编码到令牌中的数据
        expires_delta (Optional[timedelta]): 令牌过期时间增量，如果为 None 则使用默认值
    
    返回:
        str: 编码后的 JWT 令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  # 添加过期时间
    encoded_jwt = jwt.encode(to_encode, settings.TOKEN_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    验证 JWT 令牌
    
    参数:
        token (str): 要验证的 JWT 令牌
    
    返回:
        Optional[dict]: 如果验证成功返回解码后的数据，否则返回 None
    """
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        return None 
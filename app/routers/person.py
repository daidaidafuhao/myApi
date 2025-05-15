from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from ..utils.image_processing import validate_image, detect_faces
from ..core.security import verify_token

router = APIRouter()

async def get_current_user(token: str = Depends(verify_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return token

@router.post("/detect")
async def detect_person_endpoint(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # 验证图片
    if not validate_image(image):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # 读取图片
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 检测人脸
    faces = detect_faces(img)
    
    # 返回结果
    return JSONResponse(
        content={
            "status": "success",
            "people": [
                {"x": x, "y": y, "width": w, "height": h}
                for x, y, w, h in faces
            ]
        }
    ) 
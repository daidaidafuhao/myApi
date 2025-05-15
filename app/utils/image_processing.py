from PIL import Image
import cv2
import mediapipe as mp
import numpy as np
from rembg import remove
from typing import Tuple, List, Optional
from ..core.config import settings

def validate_image(file) -> bool:
    """
    验证上传的图片文件是否合法
    
    参数:
        file: 上传的文件对象
    
    返回:
        bool: 如果文件合法返回 True，否则返回 False
    
    验证内容:
        1. 文件类型是否为允许的图片格式
        2. 文件大小是否超过限制
    """
    if file.content_type not in [f"image/{ext}" for ext in settings.ALLOWED_EXTENSIONS]:
        return False
    if file.size > settings.MAX_UPLOAD_SIZE:
        return False
    return True

def detect_faces(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    使用 MediaPipe 检测图像中的人脸
    
    参数:
        image (np.ndarray): 输入图像数组
    
    返回:
        List[Tuple[int, int, int, int]]: 检测到的人脸位置列表
        每个人脸位置包含 (x, y, width, height)
    """
    mp_face_detection = mp.solutions.face_detection
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        faces = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = image.shape
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                faces.append((x, y, width, height))
        return faces

def crop_avatar(image: np.ndarray, face_box: Tuple[int, int, int, int]) -> np.ndarray:
    """
    根据人脸位置裁剪头像
    
    参数:
        image (np.ndarray): 输入图像数组
        face_box (Tuple[int, int, int, int]): 人脸位置 (x, y, width, height)
    
    返回:
        np.ndarray: 裁剪后的头像图像
    """
    x, y, w, h = face_box
    # 扩大裁剪区域，确保包含完整的人脸
    center_x = x + w // 2
    center_y = y + h // 2
    size = max(w, h) * 2  # 扩大裁剪区域为原人脸大小的两倍
    x1 = max(0, center_x - size // 2)
    y1 = max(0, center_y - size // 2)
    x2 = min(image.shape[1], x1 + size)
    y2 = min(image.shape[0], y1 + size)
    return image[y1:y2, x1:x2]

def remove_background(image: np.ndarray) -> np.ndarray:
    """
    移除图像背景，生成透明背景的 PNG 图像
    
    参数:
        image (np.ndarray): 输入图像数组
    
    返回:
        np.ndarray: 移除背景后的图像，带有透明通道
    """
    return remove(image) 
import os
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import logging
from typing import Union

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleUpscaleProcessor:
    """简单的图片高清化处理器 - 使用传统算法，无需复杂AI依赖"""
    
    def __init__(self):
        logger.info("初始化简单图片高清化处理器")
    
    def enhance_image(self, input_image: Union[str, Image.Image], output_path: str,
                     enhance_level: str = "medium") -> str:
        """
        对图片进行高清化处理（保持原尺寸，提升质量）
        
        参数:
        input_image: 输入图像（文件路径或PIL Image对象）
        output_path: 输出图像保存路径
        enhance_level: 增强级别 ("light", "medium", "strong")
        
        返回:
        str: 处理后的图像路径
        """
        try:
            # 处理输入图像
            if isinstance(input_image, str):
                logger.info(f"从文件路径加载图像: {input_image}")
                img = Image.open(input_image)
            else:
                logger.info("从PIL Image对象加载图像")
                img = input_image
            
            # 确保图像是RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_size = img.size
            logger.info(f"图像尺寸: {original_size[0]}x{original_size[1]} (保持不变)")
            
            # 进行高清化处理
            logger.info(f"开始高清化处理，增强级别: {enhance_level}")
            enhanced_img = self._enhance_quality(img, enhance_level)
            
            # 保存结果
            logger.info(f"保存处理结果到: {output_path}")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存为高质量PNG
            enhanced_img.save(output_path, 'PNG', optimize=True)
            
            logger.info("图像高清化处理完成")
            return output_path
            
        except Exception as e:
            logger.error(f"图像高清化处理失败: {str(e)}", exc_info=True)
            raise Exception(f"图像高清化处理失败: {str(e)}")
    
    def upscale_image(self, input_image: Union[str, Image.Image], output_path: str,
                     scale: int = 4, method: str = "lanczos", 
                     enhance_quality: bool = True) -> str:
        """
        对图片进行放大处理（改变尺寸）
        
        参数:
        input_image: 输入图像（文件路径或PIL Image对象）
        output_path: 输出图像保存路径
        scale: 放大倍数 (2, 4, 8)
        method: 插值方法 ("lanczos", "cubic", "linear")
        enhance_quality: 是否进行质量增强
        
        返回:
        str: 处理后的图像路径
        """
        try:
            # 处理输入图像
            if isinstance(input_image, str):
                logger.info(f"从文件路径加载图像: {input_image}")
                img = Image.open(input_image)
            else:
                logger.info("从PIL Image对象加载图像")
                img = input_image
            
            # 确保图像是RGB模式
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_size = img.size
            logger.info(f"原始图像尺寸: {original_size[0]}x{original_size[1]}")
            
            # 计算新尺寸
            new_size = (original_size[0] * scale, original_size[1] * scale)
            logger.info(f"目标尺寸: {new_size[0]}x{new_size[1]}")
            
            # 选择插值方法
            resample_method = {
                "lanczos": Image.LANCZOS,
                "cubic": Image.BICUBIC,
                "linear": Image.BILINEAR
            }.get(method.lower(), Image.LANCZOS)
            
            # 进行图像放大
            logger.info(f"开始图像放大，使用{method}插值算法")
            upscaled_img = img.resize(new_size, resample_method)
            
            # 质量增强处理
            if enhance_quality:
                logger.info("应用质量增强")
                upscaled_img = self._enhance_upscaled(upscaled_img, scale)
            
            # 保存结果
            logger.info(f"保存处理结果到: {output_path}")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存为高质量PNG
            upscaled_img.save(output_path, 'PNG', optimize=True)
            
            logger.info("图像放大处理完成")
            return output_path
            
        except Exception as e:
            logger.error(f"图像放大处理失败: {str(e)}", exc_info=True)
            raise Exception(f"图像放大处理失败: {str(e)}")
    
    def _enhance_quality(self, img: Image.Image, enhance_level: str) -> Image.Image:
        """
        对图像进行高清化处理（保持原尺寸）
        
        参数:
        img: 输入图像
        enhance_level: 增强级别
        
        返回:
        增强后的图像
        """
        try:
            # 根据增强级别设置参数
            if enhance_level == "light":
                sharpen_factor = 1.1
                contrast_factor = 1.05
                color_factor = 1.02
                denoise_strength = 3
            elif enhance_level == "strong":
                sharpen_factor = 1.4
                contrast_factor = 1.15
                color_factor = 1.08
                denoise_strength = 7
            else:  # medium
                sharpen_factor = 1.25
                contrast_factor = 1.1
                color_factor = 1.05
                denoise_strength = 5
            
            # 转换为numpy数组进行降噪
            img_array = np.array(img)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # 1. 降噪处理
            logger.info("应用降噪处理")
            img_cv = cv2.bilateralFilter(img_cv, denoise_strength, 20, 20)
            
            # 2. 细节增强（使用Unsharp Mask）
            logger.info("应用细节增强")
            gaussian = cv2.GaussianBlur(img_cv, (0, 0), 2.0)
            img_cv = cv2.addWeighted(img_cv, 1.5, gaussian, -0.5, 0)
            
            # 转换回PIL
            img_array = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img_array)
            
            # 3. 锐化处理
            logger.info("应用锐化处理")
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpen_factor)
            
            # 4. 对比度增强
            logger.info("应用对比度增强")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_factor)
            
            # 5. 色彩饱和度增强
            logger.info("应用色彩增强")
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(color_factor)
            
            return img
            
        except Exception as e:
            logger.warning(f"质量增强失败，返回原图: {str(e)}")
            return img
    
    def _enhance_upscaled(self, img: Image.Image, scale: int) -> Image.Image:
        """
        对放大后的图像进行质量增强
        """
        try:
            # 轻微的锐化处理
            sharpness_factor = min(1.2, 1.0 + (scale - 2) * 0.1)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness_factor)
            
            # 对比度微调
            contrast_factor = min(1.1, 1.0 + (scale - 2) * 0.05)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_factor)
            
            # 颜色饱和度微调
            color_factor = min(1.05, 1.0 + (scale - 2) * 0.02)
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(color_factor)
            
            return img
            
        except Exception as e:
            logger.warning(f"放大质量增强失败，返回原图: {str(e)}")
            return img
    
    def cleanup(self):
        """清理资源（简单实现无需特殊清理）"""
        logger.info("简单高清化处理器清理完成")

# 全局处理器实例
_simple_upscale_processor = None

def get_simple_upscale_processor() -> SimpleUpscaleProcessor:
    """获取全局的简单高清化处理器实例"""
    global _simple_upscale_processor
    if _simple_upscale_processor is None:
        _simple_upscale_processor = SimpleUpscaleProcessor()
    return _simple_upscale_processor 
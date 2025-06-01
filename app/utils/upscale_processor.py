import os
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, Union
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

# 设置环境变量以解决OpenMP线程冲突问题
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpscaleProcessor:
    """图片高清化处理器"""
    
    def __init__(self):
        self.model = None
        self.current_model_name = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"使用设备: {self.device}")
    
    def _load_model(self, model_name: str, scale: int = 4, tile_size: int = 512, 
                   tile_pad: int = 32, pre_pad: int = 10, half_precision: bool = False):
        """加载指定的模型"""
        if self.current_model_name == model_name and self.model is not None:
            logger.info(f"模型 {model_name} 已加载，跳过重复加载")
            return
        
        logger.info(f"正在加载模型: {model_name}")
        
        # 定义模型配置
        model_configs = {
            'RealESRGAN_x4plus': {
                'model_path': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
                'model': RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4),
                'scale': 4
            },
            'RealESRNet_x4plus': {
                'model_path': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth',
                'model': RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4),
                'scale': 4
            },
            'RealESRGAN_x2plus': {
                'model_path': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth',
                'model': RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2),
                'scale': 2
            },
            'realesr-animevideov3': {
                'model_path': 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth',
                'model': SRVGGNetCompact(num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4, act_type='prelu'),
                'scale': 4
            }
        }
        
        if model_name not in model_configs:
            raise ValueError(f"不支持的模型: {model_name}")
        
        config = model_configs[model_name]
        
        try:
            # 创建模型目录
            model_dir = "models"
            os.makedirs(model_dir, exist_ok=True)
            
            # 获取模型路径
            model_path = os.path.join(model_dir, f"{model_name}.pth")
            
            # 如果模型文件不存在，下载它
            if not os.path.exists(model_path):
                logger.info(f"正在下载模型文件...")
                load_file_from_url(config['model_path'], model_dir=model_dir, file_name=f"{model_name}.pth")
            
            # 创建RealESRGANer实例
            self.model = RealESRGANer(
                scale=config['scale'],
                model_path=model_path,
                model=config['model'],
                tile=tile_size,
                tile_pad=tile_pad,
                pre_pad=pre_pad,
                half=half_precision,
                device=self.device
            )
            
            self.current_model_name = model_name
            logger.info(f"模型 {model_name} 加载成功")
            
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            raise
    
    def upscale_image(self, input_image: Union[str, Image.Image], output_path: str,
                     scale: int = 4, model_name: str = "RealESRGAN_x4plus",
                     tile_size: int = 512, tile_pad: int = 32, pre_pad: int = 10,
                     half_precision: bool = False) -> str:
        """
        对图片进行高清化处理
        
        参数:
        input_image: 输入图像（文件路径或PIL Image对象）
        output_path: 输出图像保存路径
        scale: 放大倍数
        model_name: 使用的模型名称
        tile_size: 分块处理大小
        tile_pad: 分块边界填充
        pre_pad: 预填充大小
        half_precision: 是否使用半精度推理
        
        返回:
        str: 处理后的图像路径
        """
        try:
            # 加载模型
            self._load_model(model_name, scale, tile_size, tile_pad, pre_pad, half_precision)
            
            # 处理输入图像
            if isinstance(input_image, str):
                logger.info(f"从文件路径加载图像: {input_image}")
                img = cv2.imread(input_image, cv2.IMREAD_COLOR)
                if img is None:
                    raise ValueError(f"无法读取图像文件: {input_image}")
            else:
                # PIL Image转换为OpenCV格式
                logger.info("从PIL Image对象加载图像")
                img = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2BGR)
            
            original_height, original_width = img.shape[:2]
            logger.info(f"原始图像尺寸: {original_width}x{original_height}")
            
            # 进行高清化处理
            logger.info(f"开始高清化处理，放大倍数: {scale}x")
            output, _ = self.model.enhance(img, outscale=scale)
            
            new_height, new_width = output.shape[:2]
            logger.info(f"处理后图像尺寸: {new_width}x{new_height}")
            
            # 保存结果
            logger.info(f"保存处理结果到: {output_path}")
            cv2.imwrite(output_path, output)
            
            logger.info("图像高清化处理完成")
            return output_path
            
        except Exception as e:
            logger.error(f"图像高清化处理失败: {str(e)}", exc_info=True)
            raise Exception(f"图像高清化处理失败: {str(e)}")
    
    def cleanup(self):
        """清理资源"""
        if self.model is not None:
            del self.model
            self.model = None
            self.current_model_name = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("模型资源已清理")

# 全局处理器实例
_upscale_processor = None

def get_upscale_processor() -> UpscaleProcessor:
    """获取全局的高清化处理器实例"""
    global _upscale_processor
    if _upscale_processor is None:
        _upscale_processor = UpscaleProcessor()
    return _upscale_processor 
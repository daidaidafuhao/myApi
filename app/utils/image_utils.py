import os
import argparse
from rembg import remove, new_session
from PIL import Image
import numpy as np

def change_background(input_path, output_path, bg_color=(255, 255, 255, 255), max_size=800, model="u2net", 
                    use_alpha_matting=True, alpha_foreground=240, alpha_background=10, alpha_erode=5):
    """
    移除图像背景并替换为指定颜色
    
    参数:
    input_path: 输入图像路径
    output_path: 输出图像保存路径
    bg_color: 背景颜色，格式为(R,G,B,A)，默认为白色
    max_size: 处理时的最大尺寸，默认800像素
    model: 要使用的模型，默认为u2net
    use_alpha_matting: 是否使用alpha_matting处理边缘，默认为True
    alpha_foreground: alpha_matting前景阈值 (0-255)，值越小，保留的前景越多
    alpha_background: alpha_matting背景阈值 (0-255)，值越大，移除的背景越多
    alpha_erode: alpha_matting腐蚀尺寸，影响边缘过渡区域的大小
    """
    try:
        # 创建会话，指定模型
        print(f"正在加载{model}模型...")
        session = new_session(model)
        
        # 打开输入图像
        print(f"处理图像: {input_path}")
        input_image = Image.open(input_path)
        
        # 保存原始尺寸
        original_size = input_image.size
        print(f"原始尺寸: {original_size[0]}x{original_size[1]}")
        
        # 调整图像大小用于处理
        if max(original_size) > max_size:
            scale = max_size / max(original_size)
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            print(f"调整处理尺寸为: {new_size[0]}x{new_size[1]}")
            input_image = input_image.resize(new_size, Image.LANCZOS)
        
        # 移除背景
        if use_alpha_matting:
            print(f"移除背景中... 使用增强alpha_matting (前景={alpha_foreground}, 背景={alpha_background}, 腐蚀={alpha_erode})")
            output = remove(
                input_image,
                session=session,
                bgcolor=bg_color,
                alpha_matting=True,
                alpha_matting_foreground_threshold=alpha_foreground,
                alpha_matting_background_threshold=alpha_background,
                alpha_matting_erode_size=alpha_erode
            )
        else:
            print(f"移除背景中... 不使用alpha_matting")
            output = remove(
                input_image,
                session=session,
                bgcolor=bg_color,
                alpha_matting=False
            )
        
        # 如果之前调整了大小，现在恢复到原始尺寸
        if max(original_size) > max_size:
            print(f"恢复到原始尺寸: {original_size[0]}x{original_size[1]}")
            output = output.resize(original_size, Image.LANCZOS)
        
        # 保存结果
        print(f"保存结果到: {output_path}")
        output.save(output_path)
        print("处理完成!")
        
    except Exception as e:
        print(f"处理图像时出错: {e}")

def process_directory(input_dir, output_dir, bg_color=(255, 255, 255, 255), max_size=800, model="u2net", 
                      use_alpha_matting=True, alpha_foreground=240, alpha_background=10, alpha_erode=5):
    """处理目录中的所有图像"""
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建会话，重用会话可以加快速度
    print(f"正在加载{model}模型...")
    session = new_session(model)
    
    # 获取所有图像文件
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"在 {input_dir} 中没有找到图像文件")
        return
    
    # 处理每个图像
    for i, img_file in enumerate(image_files, 1):
        input_path = os.path.join(input_dir, img_file)
        output_path = os.path.join(output_dir, f"{os.path.splitext(img_file)[0]}_bg_changed.png")
        
        print(f"[{i}/{len(image_files)}] 处理图像: {img_file}")
        try:
            # 打开输入图像
            input_image = Image.open(input_path)
            
            # 保存原始尺寸
            original_size = input_image.size
            print(f"原始尺寸: {original_size[0]}x{original_size[1]}")
            
            # 调整图像大小用于处理
            if max(original_size) > max_size:
                scale = max_size / max(original_size)
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                print(f"调整处理尺寸为: {new_size[0]}x{new_size[1]}")
                input_image = input_image.resize(new_size, Image.LANCZOS)
            
            # 移除背景
            if use_alpha_matting:
                print(f"移除背景中... 使用增强alpha_matting (前景={alpha_foreground}, 背景={alpha_background}, 腐蚀={alpha_erode})")
                output = remove(
                    input_image,
                    session=session,
                    bgcolor=bg_color,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=alpha_foreground,
                    alpha_matting_background_threshold=alpha_background,
                    alpha_matting_erode_size=alpha_erode
                )
            else:
                print(f"移除背景中... 不使用alpha_matting")
                output = remove(
                    input_image,
                    session=session,
                    bgcolor=bg_color,
                    alpha_matting=False
                )
            
            # 如果之前调整了大小，现在恢复到原始尺寸
            if max(original_size) > max_size:
                print(f"恢复到原始尺寸: {original_size[0]}x{original_size[1]}")
                output = output.resize(original_size, Image.LANCZOS)
            
            # 保存结果
            output.save(output_path)
            print(f"已保存到: {output_path}")
            
        except Exception as e:
            print(f"处理 {img_file} 时出错: {e}")
    
    print("所有图像处理完成!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用AI模型替换图像背景颜色")
    parser.add_argument("input", help="输入图像路径或包含图像的文件夹")
    parser.add_argument("output", help="输出图像路径或输出文件夹")
    parser.add_argument("--color", help="背景颜色 (R,G,B,A)，例如: '255,0,0,255'表示红色", default="255,255,255,255")
    parser.add_argument("--max-size", type=int, help="处理时的最大尺寸（像素），默认800", default=800)
    parser.add_argument("--model", help="使用的模型，可选：u2net, u2netp, u2net_human_seg, u2net_cloth_seg, silueta 等", default="u2net")
    parser.add_argument("--no-alpha", action="store_true", help="禁用alpha_matting（处理速度更快，内存占用更少，但边缘可能不太精细）")
    parser.add_argument("--alpha-fg", type=int, help="alpha_matting前景阈值 (0-255)，值越小，保留的前景越多", default=240)
    parser.add_argument("--alpha-bg", type=int, help="alpha_matting背景阈值 (0-255)，值越大，移除的背景越多", default=10)
    parser.add_argument("--alpha-erode", type=int, help="alpha_matting腐蚀尺寸，增大该值使边缘过渡更平滑", default=5)
    
    args = parser.parse_args()
    
    # 解析背景颜色
    try:
        bg_color = tuple(map(int, args.color.split(',')))
        if len(bg_color) != 4:
            raise ValueError("颜色值必须是4个数字: R,G,B,A")
    except Exception as e:
        print(f"解析颜色值时出错: {e}")
        print("使用默认白色背景")
        bg_color = (255, 255, 255, 255)
    
    # 是否使用alpha_matting
    use_alpha_matting = not args.no_alpha
    
    # 检查是文件还是目录
    if os.path.isfile(args.input):
        change_background(args.input, args.output, bg_color, args.max_size, args.model, 
                          use_alpha_matting, args.alpha_fg, args.alpha_bg, args.alpha_erode)
    elif os.path.isdir(args.input):
        process_directory(args.input, args.output, bg_color, args.max_size, args.model,
                          use_alpha_matting, args.alpha_fg, args.alpha_bg, args.alpha_erode)
    else:
        print(f"输入路径不存在: {args.input}")
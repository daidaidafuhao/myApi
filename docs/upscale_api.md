# 图片高清化API文档

## 概述

图片高清化API提供了基于传统插值算法的图像放大服务，可以将低分辨率图片放大为高分辨率图片。虽然效果不如AI模型，但无需复杂依赖，运行稳定可靠。

## 功能特点

- 支持2x、4x、8x放大倍数
- 多种插值算法选择（Lanczos、Bicubic、Bilinear）
- 智能质量增强（锐化、对比度、降噪）
- 异步任务处理，避免长时间等待
- 无需GPU，运行稳定
- 轻量级实现，依赖简单

## API端点

### 1. 提交高清化任务

**POST** `/api/v1/upscale/enhance`

#### 请求参数

- `token` (query, required): JWT认证令牌
- `file` (form-data, required): 要处理的图片文件
- `scale` (query, optional): 放大倍数，支持2、4、8，默认4
- `method` (query, optional): 插值方法，默认"lanczos"
- `enhance_quality` (query, optional): 是否应用质量增强，默认true

#### 支持的插值方法

- `lanczos`: Lanczos插值（推荐，质量最好）
- `cubic`: 双三次插值（速度与质量平衡）
- `linear`: 双线性插值（速度最快）

#### 响应示例

```json
{
  "task_id": "abc123-def456-ghi789",
  "message": "Upscale task submitted successfully (using traditional algorithms)"
}
```

### 2. 查询任务状态

**GET** `/api/v1/upscale/status/{task_id}`

#### 请求参数

- `task_id` (path, required): 任务ID
- `token` (query, required): JWT认证令牌

#### 响应示例

```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "completed",
  "result_path": "/path/to/result.png",
  "error": null
}
```

#### 任务状态说明

- `pending`: 任务已提交，等待处理
- `processing`: 正在处理中
- `completed`: 处理完成
- `failed`: 处理失败

### 3. 下载处理结果

**GET** `/api/v1/upscale/result/{task_id}`

#### 请求参数

- `task_id` (path, required): 任务ID
- `token` (query, required): JWT认证令牌

#### 响应

成功时返回PNG格式的图片文件。

## 使用示例

### Python示例

```python
import requests
import time

# 1. 登录获取token
login_response = requests.post("http://localhost:8000/api/v1/login", params={
    "username": "test_user",
    "password": "test_password"
})
token = login_response.json()["access_token"]

# 2. 上传图片进行高清化
with open("input.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/upscale/enhance",
        files={"file": f},
        params={
            "token": token,
            "scale": 4,
            "method": "lanczos",
            "enhance_quality": True
        }
    )
task_id = response.json()["task_id"]

# 3. 等待处理完成
while True:
    status_response = requests.get(
        f"http://localhost:8000/api/v1/upscale/status/{task_id}",
        params={"token": token}
    )
    status = status_response.json()["status"]
    
    if status == "completed":
        break
    elif status == "failed":
        print("处理失败")
        break
    
    time.sleep(2)  # 传统算法处理较快，2秒检查一次即可

# 4. 下载结果
result_response = requests.get(
    f"http://localhost:8000/api/v1/upscale/result/{task_id}",
    params={"token": token}
)

with open("enhanced_output.png", "wb") as f:
    f.write(result_response.content)
```

### cURL示例

```bash
# 1. 获取token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/login?username=test_user&password=test_password" | jq -r '.access_token')

# 2. 上传图片
TASK_ID=$(curl -X POST \
  "http://localhost:8000/api/v1/upscale/enhance?token=$TOKEN&scale=4&method=lanczos&enhance_quality=true" \
  -F "file=@input.jpg" | jq -r '.task_id')

# 3. 查询状态
curl "http://localhost:8000/api/v1/upscale/status/$TASK_ID?token=$TOKEN"

# 4. 下载结果
curl "http://localhost:8000/api/v1/upscale/result/$TASK_ID?token=$TOKEN" -o enhanced_output.png
```

## 错误码说明

- `400`: 请求参数错误（如不支持的放大倍数、插值方法等）
- `401`: 认证失败，token无效
- `403`: 权限不足，无法访问指定任务
- `404`: 任务不存在或结果文件不存在
- `503`: 服务暂时不可用
- `500`: 服务器内部错误

## 算法说明

### 插值方法对比

1. **Lanczos插值**（推荐）
   - 质量最好，边缘清晰
   - 计算稍慢，但差别不大
   - 适合大多数图片类型

2. **Bicubic插值**
   - 质量较好，速度适中
   - 适合photographic图像
   - 边缘相对平滑

3. **Bilinear插值**
   - 速度最快
   - 质量较低，可能有模糊
   - 适合对速度要求高的场景

### 质量增强功能

当启用 `enhance_quality=true` 时，系统会进行：

1. **智能锐化**: 根据放大倍数调整锐化强度
2. **对比度增强**: 轻微提升图像对比度
3. **色彩饱和度**: 微调色彩表现
4. **降噪处理**: 对高倍放大图像进行降噪

## 注意事项

1. **效果限制**: 传统算法效果不如AI模型，但胜在稳定可靠
2. **处理速度**: 通常在几秒内完成，比AI方法快很多
3. **文件大小**: 建议上传图片不超过10MB
4. **适用场景**: 
   - 适合简单的图像放大需求
   - 对画质要求不是特别高的场景
   - 需要快速处理的批量操作

## 性能特点

- ✅ **无需GPU**: 纯CPU计算，成本低
- ✅ **依赖简单**: 只需PIL和OpenCV
- ✅ **速度快**: 秒级处理完成
- ✅ **稳定性高**: 不会出现AI模型的兼容性问题
- ❌ **效果有限**: 无法与先进AI模型媲美
- ❌ **细节恢复**: 无法智能恢复丢失的细节

如果您需要更高质量的AI放大效果，建议使用专门的AI图像处理服务。 
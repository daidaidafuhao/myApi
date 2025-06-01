# 背景移除+高清化组合API文档

## 概述

组合API将背景移除和图片高清化两个功能合并到一个任务中，提供一站式的人像处理服务。

**处理流程**：
1. **背景移除** - 使用AI模型去除图片背景，保留人像
2. **高清化处理** - 对去背景后的人像进行质量增强

## 功能优势

- 🎯 **一次调用，两种处理** - 省去中间步骤和文件传输
- 👤 **专注人像** - 先去背景，再高清化，效果更佳
- ⚡ **流水线处理** - 内部优化，减少I/O开销
- 🔧 **配置灵活** - 支持自定义背景移除和高清化参数

## API端点

### 提交组合任务

**POST** `/api/v1/upscale/combo`

#### 请求参数

- `token` (query, required): JWT认证令牌
- `file` (form-data, required): 要处理的图片文件
- `enhance_level` (query, optional): 高清化级别，默认"medium"
  - `light`: 轻度增强，适合质量较好的图片
  - `medium`: 中度增强，平衡质量和处理时间（推荐）
  - `strong`: 强度增强，适合质量较差的图片
- `config_id` (query, optional): 背景移除配置ID，不提供则使用默认配置

#### 响应示例

```json
{
  "task_id": "abc123-def456-ghi789",
  "message": "Background removal + enhancement combo task submitted successfully"
}
```

### 查询任务状态

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

### 下载处理结果

**GET** `/api/v1/upscale/result/{task_id}`

#### 请求参数

- `task_id` (path, required): 任务ID
- `token` (query, required): JWT认证令牌

#### 响应

成功时返回PNG格式的处理后图片文件（背景已移除的高清化人像）。

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

# 2. 上传图片进行组合处理
with open("portrait.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/upscale/combo",
        files={"file": f},
        params={
            "token": token,
            "enhance_level": "medium"
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
    
    time.sleep(5)  # 组合处理需要更长时间

# 4. 下载结果
result_response = requests.get(
    f"http://localhost:8000/api/v1/upscale/result/{task_id}",
    params={"token": token}
)

with open("enhanced_portrait.png", "wb") as f:
    f.write(result_response.content)
```

### cURL示例

```bash
# 1. 获取token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/login?username=test_user&password=test_password" | jq -r '.access_token')

# 2. 上传图片进行组合处理
TASK_ID=$(curl -X POST \
  "http://localhost:8000/api/v1/upscale/combo?token=$TOKEN&enhance_level=medium" \
  -F "file=@portrait.jpg" | jq -r '.task_id')

# 3. 查询状态
curl "http://localhost:8000/api/v1/upscale/status/$TASK_ID?token=$TOKEN"

# 4. 下载结果
curl "http://localhost:8000/api/v1/upscale/result/$TASK_ID?token=$TOKEN" -o enhanced_portrait.png
```

## 处理时间

- **纯高清化**: ~2-5秒
- **纯背景移除**: ~10-30秒  
- **组合处理**: ~15-40秒

组合处理时间 = 背景移除时间 + 高清化时间 + 少量I/O开销

## 适用场景

1. **人像摄影** - 去除杂乱背景，提升人像质量
2. **证件照处理** - 标准化背景，增强照片清晰度
3. **电商产品** - 人物模特图片处理
4. **社交媒体** - 头像美化，背景清理

## 技术特点

- ✅ **AI背景移除** - 基于深度学习模型，准确识别人物边缘
- ✅ **传统高清化** - 使用经典插值算法，稳定可靠
- ✅ **流水线优化** - 中间结果直接传递，无文件I/O
- ✅ **临时文件清理** - 自动清理中间文件，节省存储空间
- ✅ **错误处理** - 任何步骤失败都会回滚并报告

## 注意事项

1. **处理时间较长** - 包含两个处理步骤，请耐心等待
2. **适合人像** - 背景移除主要针对人物，其他主体效果可能不佳
3. **文件大小** - 建议上传图片不超过10MB
4. **结果格式** - 最终结果为PNG格式，保持透明背景

## 错误码说明

- `400`: 请求参数错误（如不支持的增强级别等）
- `401`: 认证失败，token无效
- `403`: 权限不足，无法访问指定任务
- `404`: 任务不存在或结果文件不存在
- `503`: 服务暂时不可用（高清化功能故障）
- `500`: 服务器内部错误

如需更高级的AI高清化效果，建议使用专门的AI图像处理服务。 
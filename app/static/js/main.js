// 主要功能JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const previewImage = document.getElementById('previewImage');
    const previewPlaceholder = document.getElementById('previewPlaceholder');
    const downloadBtn = document.getElementById('downloadBtn');
    const colorBtns = document.querySelectorAll('.color-btn');
    const colorPicker = document.getElementById('colorPicker');
    const processingModal = document.getElementById('processingModal');
    const progressBar = document.getElementById('progressBar');
    const processingStatus = document.getElementById('processingStatus');

    // 当前选择的背景颜色和尺寸
    let currentBackgroundColor = '#0066CC'; // 默认蓝底
    let processedImageUrl = null; // 存储处理后的图像URL
    let isProcessing = false; // 添加处理状态标志
    
    // 自动获取token
     autoLogin();
     
     // 设置定时器，每30分钟检查一次token是否即将过期
     setInterval(checkAndRefreshToken, 30 * 60 * 1000);
     
     // 检查并刷新token
     async function checkAndRefreshToken() {
         const tokenData = getTokenData();
         if (!tokenData) {
             await autoLogin();
             return;
         }
         
         // 如果token将在30分钟内过期，则刷新
         const thirtyMinutes = 30 * 60 * 1000;
         if (tokenData.expiry - Date.now() < thirtyMinutes) {
             console.log('Token即将过期，自动刷新');
             await autoLogin();
         }
     }
    
    // 自动登录获取token
    async function autoLogin() {
        try {
            // 检查是否已有token且未过期
            const tokenData = getTokenData();
            if (tokenData && tokenData.expiry > Date.now()) {
                console.log('使用现有token');
                return; // 使用现有token
            }
            
            // 需要获取新token
            const response = await fetch('/api/v1/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: 'test_user',
                    password: 'test_password'
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.access_token) {
                // 保存令牌，设置1小时过期时间
                const expiry = Date.now() + 60 * 60 * 1000; // 当前时间 + 1小时
                saveToken(data.access_token, expiry);
                console.log('自动登录成功');
            } else {
                console.error('自动登录失败:', data.error || '未知错误');
            }
        } catch (error) {
            console.error('自动登录请求失败:', error);
        }
    }
    
    // 保存token和过期时间
    function saveToken(token, expiry) {
        const tokenData = {
            token: token,
            expiry: expiry
        };
        localStorage.setItem('access_token_data', JSON.stringify(tokenData));
    }
    
    // 获取token数据
    function getTokenData() {
        const tokenDataStr = localStorage.getItem('access_token_data');
        if (!tokenDataStr) return null;
        
        try {
            return JSON.parse(tokenDataStr);
        } catch (e) {
            console.error('解析token数据失败:', e);
            return null;
        }
    }

    // 获取令牌
    function getToken() {
        const tokenData = getTokenData();
        
        // 如果没有token数据，返回null
        if (!tokenData) return null;
        
        // 检查token是否过期
        if (tokenData.expiry <= Date.now()) {
            // token已过期，尝试自动刷新
            autoLogin();
            return null;
        }
        
        return tokenData.token;
    }
    
    // 获取请求头
    function getHeaders() {
        const token = getToken();
        if (!token) {
            throw new Error('未登录或登录已过期');
        }
        return {
            'Authorization': `Bearer ${token}`
        };
    }
    
    // 显示处理进度模态框
    function showProcessingModal() {
        isProcessing = true; // 设置处理状态
        processingModal.style.display = 'block';
        progressBar.style.width = '0%';
        processingStatus.textContent = '正在处理中，请稍候...';
        
        // 更新UI状态
        dropZone.classList.add('processing');
        uploadBtn.disabled = true;
    }
    
    // 更新处理进度
    function updateProgress(percent) {
        // 平滑动画效果
        let currentWidth = parseFloat(progressBar.style.width) || 0;
        let targetWidth = percent;
        
        // 使用动画效果更平滑地更新进度条
        const animateProgress = (timestamp) => {
            if (!animateProgress.start) animateProgress.start = timestamp;
            const elapsed = timestamp - animateProgress.start;
            
            // 在500ms内完成动画
            const progress = Math.min(elapsed / 500, 1);
            const currentValue = currentWidth + progress * (targetWidth - currentWidth);
            
            progressBar.style.width = `${currentValue}%`;
            
            if (progress < 1) {
                requestAnimationFrame(animateProgress);
            }
        };
        
        requestAnimationFrame(animateProgress);
    }

    // 隐藏处理进度模态框
    function hideProcessingModal() {
        isProcessing = false; // 重置处理状态
        processingModal.style.display = 'none';
        
        // 恢复UI状态
        dropZone.classList.remove('processing');
        uploadBtn.disabled = false;
    }

    // 处理API错误
    function handleApiError(error, response) {
        console.error('API错误:', error);
        
        let errorMessage = '当前服务繁忙，请稍后再试';
        if (response) {
            // 尝试解析API返回的错误信息
            response.json().then(data => {
                if (response.status === 401) {
                    errorMessage = '登录已过期，正在重新登录...';
                    // 尝试重新登录
                    autoLogin().then(() => {
                        processingStatus.textContent = '已重新登录，请重试';
                    }).catch(() => {
                        processingStatus.textContent = errorMessage;
                    });
                } else if (response.status === 403) {
                    errorMessage = '没有权限执行此操作';
                } else if (response.status === 404) {
                    errorMessage = '请求的资源不存在';
                } else if (response.status === 413) {
                    errorMessage = '图片太大，请上传小于5MB的图片';
                } else if (response.status === 429) {
                    errorMessage = '请求过于频繁，请稍后再试';
                } else if (response.status >= 500) {
                    errorMessage = '服务器繁忙，请稍后再试';
                } else {
                    errorMessage = data.message || data.error || errorMessage;
                }
                processingStatus.textContent = errorMessage;
            }).catch(() => {
                // 如果无法解析JSON，使用HTTP状态码
                if (response.status >= 500) {
                    processingStatus.textContent = '服务器繁忙，请稍后再试';
                } else {
                    processingStatus.textContent = errorMessage;
                }
            });
        } else {
            // 网络错误或其他异常
            processingStatus.textContent = errorMessage;
        }
        
        // 显示错误一段时间后关闭模态框
        setTimeout(hideProcessingModal, 3000);
    }

    // 重置上传状态
    function resetUploadState() {
        // 清空文件输入框
        fileInput.value = '';
        
        // 释放之前的处理结果URL
        if (processedImageUrl) {
            URL.revokeObjectURL(processedImageUrl);
            processedImageUrl = null;
        }
        
        // 禁用下载按钮
        downloadBtn.disabled = true;
        
        // 清除预览图的处理结果URL
        if (previewImage.dataset.processedUrl) {
            delete previewImage.dataset.processedUrl;
        }
    }

    // 处理图片并调用API
    async function processImage(file) {
        // 如果已经在处理中，直接返回
        if (isProcessing) {
            console.log('图片正在处理中，请稍候...');
            return;
        }
        
        showProcessingModal();
        
        try {
            // 检查是否有有效token，如果没有则尝试自动登录
            let token = getToken();
            if (!token) {
                processingStatus.textContent = '正在获取授权...';
                // 尝试自动登录获取token
                await autoLogin();
                token = getToken();
                
                // 如果仍然没有token，显示错误
                if (!token) {
                    throw new Error('无法获取授权，请刷新页面重试');
                }
            }
            
            processingStatus.textContent = '正在上传文件...';
            // 准备表单数据
            const formData = new FormData();
            formData.append('file', file);
            
            // 调用背景移除API提交任务
            let response;
            try {
                response = await fetch(`/api/v1/background/remove?token=${token}`, {
                    headers: getHeaders(),
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`API错误: ${response.status}`);
                }
            } catch (error) {
                handleApiError(error, response);
                return;
            }
            
            const result = await response.json();
            const taskId = result.task_id;
            
            // 更新进度条状态
            processingStatus.textContent = '任务已提交，正在处理中...';
            updateProgress(10);
            
            // 轮询任务状态
            let isCompleted = false;
            let attempts = 0;
            const maxAttempts = 30; // 最多轮询30次
            
            while (!isCompleted && attempts < maxAttempts) {
                attempts++;
                
                // 等待1秒再查询
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // 查询任务状态
                let statusResponse;
                try {
                    statusResponse = await fetch(`/api/v1/background/status/${taskId}?token=${token}`,{
                        headers: getHeaders(),
                    });
                    
                    if (!statusResponse.ok) {
                        throw new Error(`获取状态失败: ${statusResponse.status}`);
                    }
                } catch (error) {
                    handleApiError(error, statusResponse);
                    return;
                }
                
                const statusResult = await statusResponse.json();
                
                // 更新进度 - 使用更自然的进度计算
                // 前期进度增长较慢，后期加快
                const progressPercent = Math.min(10 + Math.pow(attempts / maxAttempts, 0.7) * 80, 90);
                updateProgress(progressPercent);
                processingStatus.textContent = `正在处理中... (${attempts}/${maxAttempts})`;
                
                // 检查任务是否完成
                if (statusResult.status === 'completed') {
                    isCompleted = true;
                    
                    processingStatus.textContent = '正在获取处理结果...';
                    // 获取处理结果
                    let resultResponse;
                    try {
                        resultResponse = await fetch(`/api/v1/background/result/${taskId}?token=${token}`,{
                            headers: getHeaders(),
                        });
                        
                        if (!resultResponse.ok) {
                            throw new Error(`获取结果失败: ${resultResponse.status}`);
                        }
                    } catch (error) {
                        handleApiError(error, resultResponse);
                        return;
                    }
                    
                    const imageBlob = await resultResponse.blob();
                    
                    // 释放之前的URL（如果有的话）
                    if (processedImageUrl) {
                        URL.revokeObjectURL(processedImageUrl);
                    }
                    
                    processedImageUrl = URL.createObjectURL(imageBlob);
                    
                    // 更新预览图并应用背景色
                    try {
                        processingStatus.textContent = '正在应用背景颜色...';
                        await applyImageWithBackground(processedImageUrl);
                        updateProgress(100);
                        
                        // 启用下载按钮
                        downloadBtn.disabled = false;
                        
                        // 处理完成
                        processingStatus.textContent = '处理完成！';
                        await new Promise(resolve => setTimeout(resolve, 500));
                        hideProcessingModal();
                    } catch (error) {
                        console.error('应用背景时出错:', error);
                        throw new Error('应用背景失败: ' + error.message);
                    }
                } else if (statusResult.status === 'failed') {
                    throw new Error('处理失败: ' + (statusResult.error || '未知错误'));
                }
            }
            
            if (!isCompleted) {
                throw new Error('处理超时，请稍后再试');
            }
            
        } catch (error) {
            console.error('处理图片时出错:', error);
            processingStatus.textContent = `处理失败: ${error.message}`;
            
            // 显示错误信息3秒后关闭模态框
            setTimeout(() => {
                hideProcessingModal();
            }, 3000);
        }
    }

    // 处理上传的文件
    function handleFile(file) {
        // 检查是否正在处理
        if (isProcessing) {
            console.log('正在处理中，请稍候...');
            return;
        }
        
        if (!file.type.startsWith('image/')) {
            alert('请上传图片文件');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            alert('文件大小不能超过5MB');
            return;
        }

        // 重置之前的状态
        resetUploadState();
        
        console.log('开始处理新文件:', file.name);

        const reader = new FileReader();
        reader.onload = async (e) => {
            // 先显示原图
            previewImage.src = e.target.result;
            previewImage.classList.remove('hidden');
            previewPlaceholder.classList.add('hidden');
            
            // 开始处理图片
            await processImage(file);
        };
        
        reader.onerror = () => {
            console.error('文件读取失败');
            alert('文件读取失败，请重试');
            resetUploadState();
        };
        
        reader.readAsDataURL(file);
    }

    // 上传按钮点击事件
    uploadBtn.addEventListener('click', () => {
        // 清空文件输入框，确保change事件能触发
        fileInput.value = '';
        fileInput.click();
    });

    // 文件拖放处理
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (!isProcessing) { // 只有在非处理状态下才显示拖放效果
            dropZone.classList.add('border-blue-500');
        }
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-blue-500');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500');
        
        if (isProcessing) {
            console.log('正在处理中，请稍候...');
            return;
        }
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // 点击上传区域触发文件选择
    dropZone.addEventListener('click', () => {
        if (isProcessing) {
            console.log('正在处理中，请稍候...');
            return;
        }
        // 清空文件输入框，确保change事件能触发
        fileInput.value = '';
        fileInput.click();
    });

    // 文件选择处理
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // 尺寸转换函数（毫米转像素，300dpi）
    function mmToPx(mm) {
        return Math.round(mm * 11.81); // 300dpi换算
    }
    
    // 获取目标尺寸
    function getTargetDimensions() {
        const preset = document.getElementById('sizePreset').value;
        
        if (preset === 'custom') {
            const width = parseInt(document.getElementById('customWidth').value) || 25;
            const height = parseInt(document.getElementById('customHeight').value) || 35;
            return [mmToPx(width), mmToPx(height)];
        }
        
        const [width, height] = preset.split('x').map(Number);
        return [mmToPx(width), mmToPx(height)];
    }
    
  // 应用图片和背景色 - 改进版
async function applyImageWithBackground(imageUrl) {
    return new Promise((resolve, reject) => {
        // 首先加载透明背景的图像获取其原始尺寸和比例
        const transparentImg = new Image();
        transparentImg.onload = () => {
            // 获取原始透明图的尺寸
            const origWidth = transparentImg.width;
            const origHeight = transparentImg.height;
            const origAspectRatio = origWidth / origHeight;
            
            // 获取目标证件照尺寸
            const [targetWidth, targetHeight] = getTargetDimensions();
            const targetAspectRatio = targetWidth / targetHeight;
            
            // 创建画布 - 使用目标尺寸
            const canvas = document.createElement('canvas');
            canvas.width = targetWidth;
            canvas.height = targetHeight;
            const ctx = canvas.getContext('2d');
            
            // 填充背景色
            ctx.fillStyle = currentBackgroundColor;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 计算图像在画布上的位置和大小，保持原始图像比例
            // 但不再使用0.9的系数，而是填满整个区域
            let width, height, x, y;
            
            if (origAspectRatio > targetAspectRatio) {
                // 原图较宽，以高度为基准
                height = targetHeight;
                width = height * origAspectRatio;
                x = (targetWidth - width) / 2; // 居中放置
                y = 0;
            } else {
                // 原图较高，以宽度为基准
                width = targetWidth;
                height = width / origAspectRatio;
                x = 0;
                y = (targetHeight - height) / 2; // 居中放置
            }
            
            // 绘制透明图像
            ctx.drawImage(transparentImg, x, y, width, height);
            
            // 更新预览和存储处理后的URL
            // 使用最高质量设置 (1.0) 确保不压缩PNG图像
            try {
                const finalUrl = canvas.toDataURL('image/png', 1.0);
                previewImage.src = finalUrl;
                previewImage.classList.remove('hidden');
                previewPlaceholder.classList.add('hidden');
                previewImage.dataset.processedUrl = finalUrl;
                console.log('图像处理完成，已准备好预览和下载');
            } catch (error) {
                console.error('生成图像URL时出错:', error);
                throw new Error('无法生成图像，请重试');
            }
            
            resolve();
        };
        
        transparentImg.onerror = reject;
        transparentImg.src = imageUrl;
    });
}

// 调整预览图片在UI中的显示大小
function adjustPreviewDisplay(imgWidth, imgHeight) {
    // 获取预览区域的容器尺寸
    const container = document.getElementById('dropZone');
    const containerWidth = container.clientWidth;
    const containerHeight = container.clientHeight;
    
    // 计算图像适合容器的最大尺寸
    const containerAspect = containerWidth / containerHeight;
    const imageAspect = imgWidth / imgHeight;
    
    if (imageAspect > containerAspect) {
        // 图像较宽，以宽度为基准
        previewImage.style.width = '100%';
        previewImage.style.height = 'auto';
    } else {
        // 图像较高，以高度为基准
        previewImage.style.width = 'auto';
        previewImage.style.height = '100%';
    }
}
    // 预设颜色按钮点击事件
    colorBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const color = btn.dataset.color;
            colorPicker.value = color;
            currentBackgroundColor = color;
            
            // 如果已经有处理结果，重新应用颜色
            if (processedImageUrl) {
                await applyImageWithBackground(processedImageUrl);
            }
        });
    });

    // 自定义颜色选择事件
    colorPicker.addEventListener('change', async (e) => {
        currentBackgroundColor = e.target.value;
        
        // 如果已经有处理结果，重新应用颜色
        if (processedImageUrl) {
            await applyImageWithBackground(processedImageUrl);
        }
    });
    
    // 下载按钮点击事件
    downloadBtn.addEventListener('click', () => {
        console.log('下载按钮被点击');
        // 获取处理后的图片URL
        const processedUrl = previewImage.dataset.processedUrl;
        if (!processedUrl) {
            alert('没有可下载的图片，请先上传并处理图片');
            return;
        }
        
        try {
            console.log('开始处理下载...');
            
            // 检查URL格式
            if (!processedUrl.startsWith('data:image/')) {
                throw new Error('图像格式不正确');
            }
            
            // 方法1：使用Blob对象（主要方法）
            try {
                // 将Data URL转换为Blob对象
                const parts = processedUrl.split(',');
                const byteString = atob(parts[1]);
                const mimeType = parts[0].split(':')[1].split(';')[0];
                
                // 创建ArrayBuffer和视图
                const arrayBuffer = new ArrayBuffer(byteString.length);
                const uint8Array = new Uint8Array(arrayBuffer);
                
                for (let i = 0; i < byteString.length; i++) {
                    uint8Array[i] = byteString.charCodeAt(i);
                }
                
                // 创建Blob
                const blob = new Blob([uint8Array], {type: mimeType || 'image/png'});
                const blobUrl = URL.createObjectURL(blob);
                console.log('已创建Blob URL:', blobUrl.substring(0, 30) + '...');
                
                // 创建下载链接
                const downloadLink = document.createElement('a');
                downloadLink.href = blobUrl;
                downloadLink.download = '证件照_' + new Date().getTime() + '.png';
                downloadLink.style.display = 'none';
                document.body.appendChild(downloadLink);
                
                // 触发下载
                console.log('触发下载...');
                downloadLink.click();
                
                // 清理资源
                setTimeout(() => {
                    document.body.removeChild(downloadLink);
                    URL.revokeObjectURL(blobUrl); // 释放Blob URL
                    console.log('下载资源已清理');
                }, 1000);
                
                console.log('下载操作完成');
                return; // 如果主方法成功，直接返回
            } catch (blobError) {
                console.error('Blob下载方法失败:', blobError);
                // 如果Blob方法失败，尝试备用方法
            }
            
            // 方法2：直接使用Data URL（备用方法）
            console.log('尝试备用下载方法...');
            const downloadLink = document.createElement('a');
            downloadLink.href = processedUrl;
            downloadLink.download = '证件照_' + new Date().getTime() + '.png';
            downloadLink.style.display = 'none';
            document.body.appendChild(downloadLink);
            downloadLink.click();
            
            setTimeout(() => {
                document.body.removeChild(downloadLink);
                console.log('备用下载方法完成');
            }, 1000);
            
        } catch (error) {
            console.error('下载过程中出错:', error);
            alert('下载失败: ' + error.message + '，请重试或尝试使用不同的浏览器');
        }
    });
    
    // 监听尺寸变化事件，重新应用背景色
    document.getElementById('sizePreset').addEventListener('change', async () => {
        if (processedImageUrl) {
            await applyImageWithBackground(processedImageUrl);
        }
    });
    
    // 监听自定义尺寸输入变化
    document.getElementById('customWidth').addEventListener('change', async () => {
        if (processedImageUrl) {
            await applyImageWithBackground(processedImageUrl);
        }
    });
    
    document.getElementById('customHeight').addEventListener('change', async () => {
        if (processedImageUrl) {
            await applyImageWithBackground(processedImageUrl);
        }
    });
    
    // 移动端菜单控制
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
        
        // 点击菜单外部时关闭菜单
        document.addEventListener('click', (e) => {
            if (!mobileMenuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
        
        // 点击菜单项后关闭菜单
        const mobileMenuLinks = mobileMenu.querySelectorAll('a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
            });
        });
    }
}); 
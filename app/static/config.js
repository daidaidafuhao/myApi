// API基础URL
const API_BASE_URL = '/api/v1/config';

// 检查登录状态
function checkLogin() {
    const token = getToken();
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// 获取令牌
function getToken() {
    return localStorage.getItem('access_token');
}

// 设置请求头
function getHeaders() {
    const token = getToken();
    if (!token) {
        throw new Error('未登录或登录已过期');
    }
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// 更新滑块值显示
function updateRangeValue(input) {
    const value = input.value;
    input.nextElementSibling.textContent = value;
}

// 初始化滑块值显示
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    if (!checkLogin()) {
        return;
    }

    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        updateRangeValue(input);
        input.addEventListener('input', () => updateRangeValue(input));
    });
});

// 加载配置列表
async function loadConfigs() {
    if (!checkLogin()) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/background-configs`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            // 令牌无效，跳转到登录页面
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load configurations');
        }

        const configs = await response.json();
        const tbody = document.getElementById('configTableBody');
        
        if (tbody) {
            tbody.innerHTML = configs.map(config => `
                <tr>
                    <td>${config.name}</td>
                    <td>${config.model}</td>
                    <td>${config.max_size}</td>
                    <td>${config.use_alpha_matting ? '是' : '否'}</td>
                    <td>${config.is_default ? '是' : '否'}</td>
                    <td>${config.description || '-'}</td>
                    <td>
                        <button onclick="editConfig(${config.id})" class="btn-secondary">编辑</button>
                        <button onclick="deleteConfig(${config.id})" class="btn-secondary">删除</button>
                        ${!config.is_default ? `<button onclick="setDefault(${config.id})" class="btn-secondary">设为默认</button>` : ''}
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading configurations:', error);
        alert('加载配置失败');
    }
}

// 编辑配置
async function editConfig(id) {
    if (!checkLogin()) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/background-configs/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load configuration');
        }

        const config = await response.json();
        location.href = `config_edit.html?id=${id}`;
    } catch (error) {
        console.error('Error loading configuration:', error);
        alert('加载配置失败');
    }
}

// 删除配置
async function deleteConfig(id) {
    if (!checkLogin()) {
        return;
    }

    if (!confirm('确定要删除这个配置吗？')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/background-configs/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to delete configuration');
        }

        alert('配置已删除');
        loadConfigs();
    } catch (error) {
        console.error('Error deleting configuration:', error);
        alert('删除配置失败');
    }
}

// 设置默认配置
async function setDefault(id) {
    if (!checkLogin()) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/background-configs/${id}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify({ is_default: true })
        });
        
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to set default configuration');
        }

        alert('默认配置已更新');
        loadConfigs();
    } catch (error) {
        console.error('Error setting default configuration:', error);
        alert('设置默认配置失败');
    }
}

// 保存配置
async function saveConfig(event) {
    event.preventDefault();
    
    if (!checkLogin()) {
        return;
    }
    
    const form = event.target;
    const formData = new FormData(form);
    
    // 验证必需字段
    const name = formData.get('name');
    if (!name) {
        alert('请输入配置名称');
        return;
    }
    
    // 构建配置对象，确保所有字段都有正确的类型
    const config = {
        name: name.trim(),  // 去除空格
        model: formData.get('model') || 'u2net',
        max_size: Number(formData.get('max_size')) || 800,
        use_alpha_matting: Boolean(formData.get('use_alpha_matting') === 'on'),
        alpha_foreground: Number(formData.get('alpha_foreground')) || 240,
        alpha_background: Number(formData.get('alpha_background')) || 10,
        alpha_erode: Number(formData.get('alpha_erode')) || 15,
        is_default: Boolean(formData.get('is_default') === 'on'),
        description: formData.get('description')?.trim() || null
    };

    // 验证数值范围
    if (config.max_size < 100 || config.max_size > 2000) {
        alert('最大处理尺寸必须在100到2000之间');
        return;
    }
    if (config.alpha_foreground < 0 || config.alpha_foreground > 255) {
        alert('前景阈值必须在0到255之间');
        return;
    }
    if (config.alpha_background < 0 || config.alpha_background > 255) {
        alert('背景阈值必须在0到255之间');
        return;
    }
    if (config.alpha_erode < 0 || config.alpha_erode > 40) {
        alert('腐蚀大小必须在0到40之间');
        return;
    }

    console.log('Sending config:', config); // 添加日志

    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_BASE_URL}/background-configs/${id}` : `${API_BASE_URL}/background-configs`;

    try {
        const response = await fetch(url, {
            method: method,
            headers: getHeaders(),
            body: JSON.stringify(config)
        });
        
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Server error response:', errorData); // 添加错误日志
            throw new Error(JSON.stringify(errorData));
        }

        alert('配置已保存');
        location.href = 'config_list.html';
    } catch (error) {
        console.error('Error saving configuration:', error);
        alert('保存配置失败: ' + error.message);
    }
}

// 加载配置详情
async function loadConfigDetails() {
    if (!checkLogin()) {
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    
    if (!id) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/background-configs/${id}`, {
            headers: getHeaders()
        });
        
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            throw new Error('Failed to load configuration');
        }

        const config = await response.json();
        document.getElementById('pageTitle').textContent = '编辑配置';
        
        // 填充表单
        Object.keys(config).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = config[key];
                } else {
                    element.value = config[key];
                }
            }
        });

        // 更新滑块值显示
        document.querySelectorAll('input[type="range"]').forEach(input => {
            updateRangeValue(input);
        });
    } catch (error) {
        console.error('Error loading configuration:', error);
        alert('加载配置失败');
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 加载配置列表
    if (document.getElementById('configTableBody')) {
        loadConfigs();
    }
    
    // 加载配置详情
    if (document.getElementById('configForm')) {
        loadConfigDetails();
        document.getElementById('configForm').addEventListener('submit', saveConfig);
    }
}); 
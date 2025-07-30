// API服务器地址配置
const API_BASE_URL = 'http://localhost:5000/api';

// 页面元素
const flowAnalysisForm = document.getElementById('flowAnalysisForm');
const networkAnalysisForm = document.getElementById('networkAnalysisForm');
const analysisDescription = document.getElementById('analysisDescription');
const alertContainer = document.getElementById('alert-container');

// 工具函数
function showAlert(message, type = 'danger') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alertDiv);
    
    // 自动消失
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function hideAlert() {
    alertContainer.innerHTML = '';
}

// 分析类型切换
document.getElementById('flowAnalysis').addEventListener('change', function() {
    if (this.checked) {
        flowAnalysisForm.style.display = 'block';
        networkAnalysisForm.style.display = 'none';
        analysisDescription.textContent = '分析单个Excel文件的交易数据，生成统计图表和报告';
    }
});

document.getElementById('networkAnalysis').addEventListener('change', function() {
    if (this.checked) {
        flowAnalysisForm.style.display = 'none';
        networkAnalysisForm.style.display = 'block';
        analysisDescription.textContent = '分析多个Excel文件，生成资金流向网络图，限制节点数不超过150个';
    }
});

// 流水分析文件上传处理
const flowFileInput = document.getElementById('flowFileInput');
const flowFileName = document.getElementById('flowFileName');
const flowFileNameText = document.getElementById('flowFileNameText');
const flowUploadBtn = document.getElementById('flowUploadBtn');
const flowUploadArea = document.getElementById('flowUploadArea');

flowFileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
        flowFileNameText.textContent = this.files[0].name;
        flowFileName.style.display = 'block';
        flowUploadBtn.disabled = false;
    } else {
        flowFileName.style.display = 'none';
        flowUploadBtn.disabled = true;
    }
});

// 网络分析文件上传处理
const networkFileInput = document.getElementById('networkFileInput');
const networkFileName = document.getElementById('networkFileName');
const networkFileNameText = document.getElementById('networkFileNameText');
const networkUploadBtn = document.getElementById('networkUploadBtn');
const networkUploadArea = document.getElementById('networkUploadArea');

networkFileInput.addEventListener('change', function() {
    if (this.files && this.files.length > 0) {
        const fileNames = Array.from(this.files).map(file => file.name);
        networkFileNameText.textContent = `已选择 ${this.files.length} 个文件: ${fileNames.join(', ')}`;
        networkFileName.style.display = 'block';
        networkUploadBtn.disabled = false;
    } else {
        networkFileName.style.display = 'none';
        networkUploadBtn.disabled = true;
    }
});

// 拖拽上传功能 - 流水分析
flowUploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('bg-light');
});

flowUploadArea.addEventListener('dragleave', function(e) {
    e.preventDefault();
    this.classList.remove('bg-light');
});

flowUploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('bg-light');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            flowFileInput.files = files;
            flowFileNameText.textContent = file.name;
            flowFileName.style.display = 'block';
            flowUploadBtn.disabled = false;
        } else {
            showAlert('请上传Excel格式的文件(.xlsx或.xls)', 'warning');
        }
    }
});

// 拖拽上传功能 - 网络分析
networkUploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('bg-light');
});

networkUploadArea.addEventListener('dragleave', function(e) {
    e.preventDefault();
    this.classList.remove('bg-light');
});

networkUploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('bg-light');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const validFiles = Array.from(files).filter(file => 
            file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
        );
        if (validFiles.length > 0) {
            networkFileInput.files = files;
            const fileNames = validFiles.map(file => file.name);
            networkFileNameText.textContent = `已选择 ${validFiles.length} 个文件: ${fileNames.join(', ')}`;
            networkFileName.style.display = 'block';
            networkUploadBtn.disabled = false;
        } else {
            showAlert('请上传Excel格式的文件(.xlsx或.xls)', 'warning');
        }
    }
});

// 流水分析表单提交
flowAnalysisForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    hideAlert();
    
    const file = flowFileInput.files[0];
    if (!file) {
        showAlert('请选择要上传的文件', 'warning');
        return;
    }
    
    // 显示加载状态
    flowUploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>分析中...';
    flowUploadBtn.disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(result.message || '文件分析完成！', 'success');
            // 跳转到结果页面
            sessionStorage.setItem('analysisResult', JSON.stringify(result));
            sessionStorage.setItem('analysisType', 'flow');
            window.location.href = 'results.html';
        } else {
            showAlert(result.error || '分析失败，请重试', 'danger');
        }
    } catch (error) {
        console.error('上传错误:', error);
        showAlert('网络错误，请检查后端服务是否启动', 'danger');
    } finally {
        // 恢复按钮状态
        flowUploadBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>开始流水分析';
        flowUploadBtn.disabled = false;
    }
});

// 网络分析表单提交
networkAnalysisForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    hideAlert();
    
    const files = networkFileInput.files;
    if (!files || files.length === 0) {
        showAlert('请选择要上传的文件', 'warning');
        return;
    }
    
    // 显示加载状态
    networkUploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>分析中...';
    networkUploadBtn.disabled = true;
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload_network`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(result.message || '网络图分析完成！', 'success');
            // 跳转到网络结果页面
            sessionStorage.setItem('analysisResult', JSON.stringify(result));
            sessionStorage.setItem('analysisType', 'network');
            window.location.href = 'network-results.html';
        } else {
            showAlert(result.error || '分析失败，请重试', 'danger');
        }
    } catch (error) {
        console.error('上传错误:', error);
        showAlert('网络错误，请检查后端服务是否启动', 'danger');
    } finally {
        // 恢复按钮状态
        networkUploadBtn.innerHTML = '<i class="fas fa-project-diagram me-2"></i>开始网络分析';
        networkUploadBtn.disabled = false;
    }
});

// 页面加载时检查后端服务状态
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('后端API服务正常运行');
        } else {
            showAlert('后端服务连接异常，请检查服务是否启动', 'warning');
        }
    } catch (error) {
        showAlert('无法连接到后端服务，请确保后端API服务已启动', 'warning');
        console.error('后端服务检查失败:', error);
    }
});
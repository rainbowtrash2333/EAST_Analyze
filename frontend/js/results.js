// API服务器地址配置
const API_BASE_URL = 'http://localhost:5000/api';

// 页面加载时获取分析结果
document.addEventListener('DOMContentLoaded', function() {
    const analysisResult = JSON.parse(sessionStorage.getItem('analysisResult'));
    const analysisType = sessionStorage.getItem('analysisType');
    
    if (!analysisResult || analysisType !== 'flow') {
        alert('没有找到分析结果，请重新分析');
        window.location.href = 'index.html';
        return;
    }
    
    loadResults(analysisResult);
});

function loadResults(result) {
    // 显示文件名
    document.getElementById('filename-display').textContent = `文件：${result.filename}`;
    
    // 加载整体统计
    loadTotalStats(result.total_stats);
    
    // 加载图表
    loadCharts(result.chart_files);
    
    // 加载交易对手数据
    loadCounterpartyData(result.counterparty_stats);
    
    // 加载交易类型数据
    loadTransactionTypeData(result.transaction_type_stats);
    
    // 加载交易渠道数据
    loadChannelData(result.channel_stats);
    
    // 生成下载链接
    generateDownloadLinks(result);
}

function loadTotalStats(totalStats) {
    const container = document.getElementById('total-stats-container');
    container.innerHTML = '';
    
    totalStats.forEach(stat => {
        const col = document.createElement('div');
        col.className = 'col-md-2 col-sm-4 col-6';
        
        const value = typeof stat['数值'] === 'number' ? stat['数值'].toFixed(2) : stat['数值'];
        
        col.innerHTML = `
            <div class="stat-card">
                <h4 class="text-primary">${value}</h4>
                <p class="mb-0 text-muted">${stat['统计指标']}</p>
            </div>
        `;
        
        container.appendChild(col);
    });
}

function loadCharts(chartFiles) {
    const mainChartsContainer = document.getElementById('main-charts-container');
    const hourlyChartsContainer = document.getElementById('hourly-charts-container');
    
    mainChartsContainer.innerHTML = '';
    hourlyChartsContainer.innerHTML = '';
    
    chartFiles.forEach(chartFile => {
        const img = document.createElement('img');
        img.src = `${API_BASE_URL}/charts/${chartFile}`;
        img.className = 'chart-img';
        img.alt = '分析图表';
        
        if (chartFile.includes('main_analysis')) {
            mainChartsContainer.appendChild(img);
        } else if (chartFile.includes('hourly_analysis')) {
            hourlyChartsContainer.appendChild(img);
        }
    });
}

function loadCounterpartyData(counterpartyStats) {
    const tbody = document.getElementById('counterparty-table');
    tbody.innerHTML = '';
    
    counterpartyStats.forEach((row, index) => {
        if (index >= 10) return; // 只显示前10个
        
        const tr = document.createElement('tr');
        
        // 净方向样式
        let badgeClass = 'badge-secondary';
        if (row['净方向'] === '净收入') badgeClass = 'badge-success';
        else if (row['净方向'] === '净支出') badgeClass = 'badge-danger';
        
        // 总交易金额颜色
        let amountClass = '';
        if (row['总交易金额'] > 0) amountClass = 'text-success';
        else if (row['总交易金额'] < 0) amountClass = 'text-danger';
        
        tr.innerHTML = `
            <td><span class="badge bg-primary">${index + 1}</span></td>
            <td><strong>${row['对方户名']}</strong></td>
            <td>${row['交易次数']}</td>
            <td class="${amountClass}">¥${row['总交易金额'].toFixed(2)}</td>
            <td><span class="badge ${badgeClass}">${row['净方向']}</span></td>
            <td class="text-success">¥${row['总收入'].toFixed(2)}</td>
            <td class="text-danger">¥${row['总支出'].toFixed(2)}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

function loadTransactionTypeData(transactionTypeStats) {
    const tbody = document.getElementById('transaction-type-table');
    tbody.innerHTML = '';
    
    transactionTypeStats.forEach(row => {
        const tr = document.createElement('tr');
        
        let amountClass = '';
        if (row['总金额'] > 0) amountClass = 'text-success';
        else if (row['总金额'] < 0) amountClass = 'text-danger';
        
        tr.innerHTML = `
            <td>${row['交易类型']}</td>
            <td>${row['交易次数']}</td>
            <td class="${amountClass}">¥${row['总金额'].toFixed(2)}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

function loadChannelData(channelStats) {
    const tbody = document.getElementById('channel-table');
    tbody.innerHTML = '';
    
    channelStats.forEach(row => {
        const tr = document.createElement('tr');
        
        let amountClass = '';
        if (row['总金额'] > 0) amountClass = 'text-success';
        else if (row['总金额'] < 0) amountClass = 'text-danger';
        
        tr.innerHTML = `
            <td>${row['交易渠道']}</td>
            <td>${row['交易次数']}</td>
            <td class="${amountClass}">¥${row['总金额'].toFixed(2)}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

function generateDownloadLinks(result) {
    const container = document.getElementById('download-links');
    container.innerHTML = '';
    
    // Excel报告下载链接
    if (result.report_file) {
        const excelLink = document.createElement('a');
        excelLink.href = `${API_BASE_URL}/download/${result.report_file}`;
        excelLink.className = 'btn-download';
        excelLink.innerHTML = '<i class="fas fa-file-excel me-2"></i>下载Excel报告';
        container.appendChild(excelLink);
    }
    
    // 图表下载链接
    if (result.chart_files) {
        result.chart_files.forEach((chartFile, index) => {
            const chartLink = document.createElement('a');
            chartLink.href = `${API_BASE_URL}/charts/${chartFile}`;
            chartLink.className = 'btn-download';
            chartLink.download = chartFile;
            chartLink.innerHTML = `<i class="fas fa-image me-2"></i>下载图表 ${index + 1}`;
            container.appendChild(chartLink);
        });
    }
}
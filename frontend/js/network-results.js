// API服务器地址配置
const API_BASE_URL = 'http://localhost:5000/api';

// 页面加载时获取分析结果
document.addEventListener('DOMContentLoaded', function() {
    const analysisResult = JSON.parse(sessionStorage.getItem('analysisResult'));
    const analysisType = sessionStorage.getItem('analysisType');
    
    if (!analysisResult || analysisType !== 'network') {
        alert('没有找到网络分析结果，请重新分析');
        window.location.href = 'index.html';
        return;
    }
    
    loadNetworkResults(analysisResult);
});

function loadNetworkResults(result) {
    // 显示文件名
    document.getElementById('filename-display').textContent = `分析文件：${result.filename}`;
    
    // 加载网络统计
    loadNetworkStats(result);
    
    // 加载网络图
    loadNetworkGraph(result.html_file);
    
    // 加载TOP账户数据
    loadTopAccounts(result.stats.top_accounts);
    
    // 加载TOP交易对手数据
    loadTopCounterparties(result.stats.top_counterparties);
    
    // 加载网络分析详情
    if (result.network_analysis) {
        loadNetworkAnalysis(result.network_analysis);
    }
}

function loadNetworkStats(result) {
    const container = document.getElementById('network-stats-container');
    container.innerHTML = '';
    
    const stats = [
        { label: '节点数量', value: result.node_count, icon: 'fas fa-circle' },
        { label: '连接数量', value: result.edge_count, icon: 'fas fa-arrows-alt-h' },
        { label: '总交易金额', value: `¥${result.stats.total_amount.toLocaleString()}`, icon: 'fas fa-dollar-sign' },
        { label: '平均交易金额', value: `¥${result.stats.avg_amount.toFixed(2)}`, icon: 'fas fa-chart-line' },
        { label: '借方交易总额', value: `¥${result.stats.borrow_stats.total.toLocaleString()}`, icon: 'fas fa-arrow-down', color: 'danger' },
        { label: '贷方交易总额', value: `¥${result.stats.lend_stats.total.toLocaleString()}`, icon: 'fas fa-arrow-up', color: 'success' }
    ];
    
    stats.forEach(stat => {
        const col = document.createElement('div');
        col.className = 'col-md-2 col-sm-4 col-6';
        
        const colorClass = stat.color ? `text-${stat.color}` : 'text-primary';
        
        col.innerHTML = `
            <div class="stat-card">
                <div class="${colorClass} mb-2">
                    <i class="${stat.icon}" style="font-size: 2rem;"></i>
                </div>
                <h5 class="${colorClass}">${stat.value}</h5>
                <p class="mb-0 text-muted small">${stat.label}</p>
            </div>
        `;
        
        container.appendChild(col);
    });
}

function loadNetworkGraph(htmlFile) {
    const iframe = document.getElementById('network-iframe');
    iframe.src = `${API_BASE_URL}/networks/${htmlFile}`;
    
    // 处理iframe加载错误
    iframe.onerror = function() {
        iframe.style.display = 'none';
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-warning text-center';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            网络图加载失败，请检查后端服务状态
        `;
        iframe.parentNode.insertBefore(errorDiv, iframe);
    };
}

function loadTopAccounts(topAccounts) {
    const tbody = document.getElementById('top-accounts-table');
    tbody.innerHTML = '';
    
    if (!topAccounts || Object.keys(topAccounts).length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">暂无数据</td></tr>';
        return;
    }
    
    const accounts = Object.entries(topAccounts).slice(0, 10);
    
    accounts.forEach(([accountName, data], index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="badge bg-primary">${index + 1}</span></td>
            <td><strong>${accountName}</strong></td>
            <td class="text-success">¥${data['交易金额'].toLocaleString()}</td>
            <td>${data['交易次数']}</td>
        `;
        tbody.appendChild(tr);
    });
}

function loadTopCounterparties(topCounterparties) {
    const tbody = document.getElementById('top-counterparties-table');
    tbody.innerHTML = '';
    
    if (!topCounterparties || Object.keys(topCounterparties).length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">暂无数据</td></tr>';
        return;
    }
    
    const counterparties = Object.entries(topCounterparties).slice(0, 10);
    
    counterparties.forEach(([counterpartyName, data], index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="badge bg-success">${index + 1}</span></td>
            <td><strong>${counterpartyName}</strong></td>
            <td class="text-success">¥${data['交易金额'].toLocaleString()}</td>
            <td>${data['交易次数']}</td>
        `;
        tbody.appendChild(tr);
    });
}

function loadNetworkAnalysis(networkAnalysis) {
    if (!networkAnalysis) return;
    
    const section = document.getElementById('network-analysis-section');
    const content = document.getElementById('network-analysis-content');
    
    section.style.display = 'block';
    
    let analysisHtml = `
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-sitemap me-2"></i>基本网络信息</h5>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between">
                        <span>节点数量</span>
                        <strong>${networkAnalysis.node_count}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>边数量</span>
                        <strong>${networkAnalysis.edge_count}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>连通分量数</span>
                        <strong>${networkAnalysis.connected_components_count}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>网络密度</span>
                        <strong>${networkAnalysis.density.toFixed(4)}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>是否有向图</span>
                        <strong>${networkAnalysis.is_directed ? '是' : '否'}</strong>
                    </li>
                </ul>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-crown me-2"></i>度中心性 TOP5</h5>
                <ul class="list-group list-group-flush">
    `;
    
    if (networkAnalysis.degree_centrality_top10 && networkAnalysis.degree_centrality_top10.length > 0) {
        networkAnalysis.degree_centrality_top10.slice(0, 5).forEach(([node, centrality], index) => {
            analysisHtml += `
                <li class="list-group-item d-flex justify-content-between">
                    <span><span class="badge bg-warning me-2">${index + 1}</span>${node}</span>
                    <strong>${centrality.toFixed(4)}</strong>
                </li>
            `;
        });
    } else {
        analysisHtml += '<li class="list-group-item text-muted">暂无数据</li>';
    }
    
    analysisHtml += `
                </ul>
            </div>
        </div>
    `;
    
    // 添加介数中心性
    if (networkAnalysis.betweenness_centrality_top10 && networkAnalysis.betweenness_centrality_top10.length > 0) {
        analysisHtml += `
            <div class="row mt-4">
                <div class="col-12">
                    <h5><i class="fas fa-route me-2"></i>介数中心性 TOP5</h5>
                    <ul class="list-group list-group-flush">
        `;
        
        networkAnalysis.betweenness_centrality_top10.slice(0, 5).forEach(([node, centrality], index) => {
            analysisHtml += `
                <li class="list-group-item d-flex justify-content-between">
                    <span><span class="badge bg-info me-2">${index + 1}</span>${node}</span>
                    <strong>${centrality.toFixed(4)}</strong>
                </li>
            `;
        });
        
        analysisHtml += `
                    </ul>
                </div>
            </div>
        `;
    }
    
    // 添加社区信息
    if (networkAnalysis.communities && networkAnalysis.communities.length > 0) {
        analysisHtml += `
            <div class="row mt-4">
                <div class="col-12">
                    <h5><i class="fas fa-users me-2"></i>社区检测结果</h5>
                    <p class="text-muted">检测到 ${networkAnalysis.communities.length} 个社区</p>
                    <div class="row">
        `;
        
        networkAnalysis.communities.slice(0, 6).forEach((community, index) => {
            analysisHtml += `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-header">
                            <strong>社区 ${community.id + 1}</strong>
                            <span class="badge bg-secondary ms-2">${community.size} 个节点</span>
                        </div>
                        <div class="card-body">
                            <small class="text-muted">
                                ${community.nodes.slice(0, 3).join(', ')}
                                ${community.nodes.length > 3 ? '...' : ''}
                            </small>
                        </div>
                    </div>
                </div>
            `;
        });
        
        analysisHtml += `
                    </div>
                </div>
            </div>
        `;
    }
    
    content.innerHTML = analysisHtml;
}
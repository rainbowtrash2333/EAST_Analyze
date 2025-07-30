# 银行流水分析系统 - 前后端分离版本

本项目已成功改造为前后端分离架构，提供更好的可维护性和扩展性。

## 项目结构

```
EAST_Analyze/
├── backend/                    # 后端API服务
│   ├── api.py                  # Flask API服务器
│   ├── analysis.py             # 数据分析模块
│   ├── network_analysis.py     # 网络分析模块
│   ├── requirements.txt        # Python依赖
│   └── README.md              # 后端文档
├── frontend/                   # 前端Web应用
│   ├── index.html             # 主页面
│   ├── results.html           # 流水分析结果页
│   ├── network-results.html   # 网络分析结果页
│   ├── js/                    # JavaScript文件
│   │   ├── app.js
│   │   ├── results.js
│   │   └── network-results.js
│   └── README.md              # 前端文档
├── static/                     # 静态文件（图表、网络图）
├── uploads/                    # 文件上传目录
├── outputs/                    # 输出文件目录
├── app.py                     # 原始Flask应用（兼容性保留）
├── analysis.py                # 原始分析模块（兼容性保留）
├── network_analysis.py        # 原始网络分析模块（兼容性保留）
├── templates/                 # 原始模板（兼容性保留）
└── README.md                  # 项目总体文档
```

## 架构特点

### 后端 (Flask API)
- **RESTful API设计**：所有接口返回JSON格式数据
- **CORS支持**：允许跨域请求，支持前后端分离部署
- **健康检查**：提供 `/api/health` 接口检查服务状态
- **文件处理**：支持单文件和多文件上传
- **错误处理**：统一的错误响应格式

### 前端 (纯静态Web应用)
- **响应式设计**：基于Bootstrap 5的现代化界面
- **异步通信**：使用Fetch API与后端交互
- **状态管理**：使用sessionStorage管理分析结果
- **错误处理**：友好的错误提示和状态反馈

## 快速开始

### 方式一：前后端分离部署（推荐）

#### 1. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
python api.py
```
后端服务将在 http://localhost:5000 启动

#### 2. 启动前端服务
可以使用任何Web服务器托管前端文件，例如：

**使用Python内置服务器：**
```bash
cd frontend
python -m http.server 8080
```

**使用Node.js http-server：**
```bash
cd frontend
npx http-server -p 8080
```

前端应用将在 http://localhost:8080 可访问

### 方式二：传统整体部署（兼容）

```bash
pip install -r requirements.txt
python app.py
```
应用将在 http://localhost:5000 启动

## 功能特色

### 流水分析模式
- 📊 **交易对手分析** - 统计各交易对手的交易次数、金额和收支情况
- 📈 **交易类型统计** - 分析不同交易类型的使用频率和金额分布  
- 📅 **时间趋势分析** - 展示每日和每小时的交易趋势
- 🔍 **多维度统计** - 提供整体统计、渠道分析等多角度洞察
- 📋 **Excel报告** - 自动生成详细的Excel分析报告
- 🖼️ **可视化图表** - 生成多种类型的统计图表

### 网络图分析模式
- 🕸️ **资金流向网络图** - 基于多个Excel文件生成交互式网络图
- 🎯 **智能节点限制** - 自动限制节点数不超过150个，确保图表可读性
- 🔴 **资金流向可视化** - 红色表示资金流出，绿色表示资金流入
- 📊 **网络统计分析** - 提供节点数、连接数、核心账户等统计信息
- 🔬 **深度网络分析** - 度中心性、介数中心性、社区检测、聚类系数分析
- 🏘️ **社区发现** - 自动识别资金流动的社区结构

## API接口

### 基础接口
- `GET /api/health` - 健康检查
- `POST /api/upload` - 单文件流水分析
- `POST /api/upload_network` - 多文件网络分析

### 文件接口  
- `GET /api/download/<filename>` - 下载Excel报告
- `GET /api/charts/<filename>` - 获取分析图表
- `GET /api/networks/<filename>` - 获取网络图

## 文件格式要求

### 流水分析文件格式
Excel文件需要包含以下列：
- 交易借贷标志、交易金额、对方户名、对方账号、对方行名
- 现转标志、交易类型、交易渠道、核心交易日期、核心交易时间

### 网络图分析文件格式
Excel文件需要包含以下列：
- 账户名称、借贷标志、对方户名、交易金额
- 可选：证件号码（用于深度网络分析）

## 主要改进

1. **架构分离**：前端和后端完全独立，可分别部署和扩展
2. **API优化**：统一的JSON响应格式，更好的错误处理
3. **用户体验**：异步加载，实时状态反馈，更好的错误提示
4. **可维护性**：代码组织更清晰，职责分离明确
5. **扩展性**：支持独立部署，方便后续功能扩展
6. **兼容性**：保留原有代码结构，支持传统部署方式

## 部署建议

### 开发环境
- 后端：直接运行Python脚本
- 前端：使用开发服务器托管静态文件

### 生产环境
- 后端：使用Gunicorn + Nginx部署Flask应用
- 前端：使用Nginx托管静态文件
- 数据库：考虑添加Redis缓存和数据库存储

## 技术栈

- **后端**：Python + Flask + pandas + matplotlib + networkx
- **前端**：HTML5 + CSS3 + JavaScript (ES6+) + Bootstrap 5
- **通信**：RESTful API + JSON
- **可视化**：matplotlib (后端) + 动态图表展示 (前端)

## 注意事项

- 支持的文件格式：.xlsx, .xls
- 最大文件大小：16MB
- 分析完成后会自动清理临时文件
- 前后端分离版本需要同时启动两个服务

## 更新日志

### v3.0 (最新) - 前后端分离版本
- 重构为前后端分离架构
- 新增RESTful API接口
- 优化前端用户体验
- 支持独立部署和扩展
- 保持向后兼容性

### v2.1 
- 新增深度网络分析功能
- 度中心性和介数中心性分析
- 基于Louvain算法的社区检测

### v2.0
- 新增网络图分析功能
- 支持多文件上传处理
- 智能节点数量限制

### v1.0
- 基础流水分析功能
- 统计图表生成
- Excel报告导出
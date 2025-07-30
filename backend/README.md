# 银行流水分析系统 - 后端API

这是银行流水分析系统的后端API服务，提供数据分析和文件处理功能。

## 功能特性

- 银行流水Excel文件分析
- 多文件网络图分析
- 数据可视化图表生成
- Excel报告生成和下载
- RESTful API接口

## API接口

### 健康检查
- `GET /api/health` - 检查后端服务状态

### 流水分析
- `POST /api/upload` - 上传单个Excel文件进行流水分析

### 网络分析  
- `POST /api/upload_network` - 上传多个Excel文件进行网络图分析

### 文件下载
- `GET /api/download/<filename>` - 下载Excel报告文件
- `GET /api/charts/<filename>` - 获取分析图表
- `GET /api/networks/<filename>` - 获取网络图文件

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行后端服务：
```bash
python api.py
```

后端服务将在 http://localhost:5000 启动。

## 环境要求

- Python 3.8+
- Flask 2.3+
- pandas, numpy, matplotlib等数据处理库

## 配置

- 上传文件大小限制：16MB
- 支持文件格式：.xlsx, .xls
- CORS已启用，支持跨域请求
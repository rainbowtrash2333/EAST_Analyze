# 银行流水分析系统 - 前端应用

这是银行流水分析系统的前端应用，提供用户友好的界面来上传文件和查看分析结果。

## 功能特性

- 响应式Web界面设计
- 支持拖拽上传Excel文件
- 流水分析和网络图分析两种模式
- 实时分析结果展示
- 可视化图表和数据表格
- 文件下载功能

## 文件结构

```
frontend/
├── index.html              # 主页面 - 文件上传界面
├── results.html            # 流水分析结果页面
├── network-results.html    # 网络图分析结果页面
└── js/
    ├── app.js              # 主页面JavaScript逻辑
    ├── results.js          # 流水分析结果页面JavaScript
    └── network-results.js  # 网络图分析结果页面JavaScript
```

## 使用方法

1. 确保后端API服务已启动（默认运行在 http://localhost:5000）

2. 使用Web服务器托管前端文件，或者直接用浏览器打开 `index.html`

3. 选择分析类型：
   - **流水分析**：上传单个Excel文件进行详细的交易流水分析
   - **网络图分析**：上传多个Excel文件生成资金流向网络图

4. 上传文件后系统会自动跳转到相应的结果页面

## 配置

在 `js/app.js` 中可以修改后端API服务器地址：

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

## 浏览器兼容性

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## 依赖

- Bootstrap 5.1.3 (CSS框架)
- Font Awesome 6.0.0 (图标)

所有依赖都通过CDN加载，无需本地安装。
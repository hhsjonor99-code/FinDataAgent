---
name: findata-agent
description: 智能金融数据助手，支持自然语言驱动的金融数据分析、Tushare数据获取、图表生成和数据导出。使用DeepSeek LLM自动生成Python代码，集成Tushare Pro API，基于Streamlit构建聊天式界面。适用于股票分析、经济指标查询、技术图表绘制、Excel数据导出等金融数据处理任务。
---

# FinDataAgent 智能金融数据助手

## 核心工作流

FinDataAgent采用"代码解释器"工作流，根据用户意图自动生成并执行Python代码：

1. **意图解析** - 分析用户自然语言需求
2. **代码生成** - DeepSeek LLM生成完整Python脚本
3. **依赖注入** - 自动添加Tushare token、matplotlib配置等
4. **脚本执行** - 安全执行并捕获输出文件
5. **结果展示** - 在Streamlit界面显示图表和数据

## 快速开始

### 环境配置
```bash
# 使用uv安装依赖
uv sync

# 配置.env文件
TUSHARE_TOKEN=你的Tushare密钥
DEEPSEEK_API_KEY=你的DeepSeek密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

### 启动应用
```bash
# Windows启动
start_app.bat

# 命令行启动
uv run streamlit run gui/app.py
```

## 核心功能使用

### 1. 自然语言数据分析
直接输入分析需求，系统自动生成代码：

**示例指令：**
- "分析贵州茅台近一年的股价趋势"
- "获取600519.SH在2023-01-01至2023-01-31的日线数据并导出Excel"
- "绘制中国GDP季度数据从2018Q1到2019Q3的折线图"

### 2. Tushare数据接口
系统内置Tushare Schema知识库，自动处理接口参数：

**支持的数据类型：**
- 股票行情（日线、周线、月线）
- 财务数据（资产负债表、利润表、现金流量表）
- 经济指标（GDP、CPI、PMI等）
- 行业数据、概念板块等

**参考文档：** [Tushare Schema](references/tushare_schema.md)

### 3. 图表生成
自动配置matplotlib无交互后端，支持多种图表类型：

**常用图表：**
- 折线图（价格趋势、时间序列）
- K线图（股票OHLC数据）
- 柱状图（成交量、财务指标）
- 散点图（相关性分析）

**图表配置脚本：** [scripts/chart_setup.py](scripts/chart_setup.py)

### 4. 数据导出
自动创建输出目录并导出多种格式：

**导出格式：**
- Excel (.xlsx) - 结构化数据表格
- CSV - 通用数据格式
- 图片 (.png/.jpg) - 图表文件

**输出路径：** `workspace/exports/`

## 技术架构

### 核心组件
- **agent_engine.py** - 主工作流引擎，实现流式输出
- **code_executor.py** - 代码执行器，注入依赖并安全执行
- **knowledge_manager.py** - 知识库检索和聚合
- **config_manager.py** - 配置管理和持久化

### 前端界面
- **app.py** - Streamlit主应用
- **chat.py** - 聊天组件
- **result_card.py** - 结果展示卡片
- **theme.py** - 主题和CSS样式

### 代码执行环境
系统自动配置执行环境：
```python
# 自动注入的依赖
import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Tushare token初始化
ts.set_token('YOUR_TOKEN')

# Matplotlib无交互后端
plt.switch_backend('Agg')
```

## 故障排除

### 常见问题
1. **Tushare API限制** - 检查token积分和调用频率
2. **代码执行失败** - 查看agent.log详细错误信息
3. **图表不显示** - 确认matplotlib后端配置
4. **导出文件为空** - 检查数据获取和过滤条件

### 日志查看
```bash
# 查看agent日志
tail -f core/agent_log_record/agent.log

# 前端日志显示在聊天界面侧边栏
```

## 扩展开发

### 添加新的数据源
1. 在`knowledge_base/`添加新的API文档
2. 更新`code_executor.py`注入新的依赖
3. 测试自然语言到代码的转换

### 自定义图表类型
1. 在`scripts/`添加新的图表模板
2. 更新知识库描述新图表的用法
3. 验证LLM生成代码的正确性

### 界面定制
1. 修改`gui/styles/theme.py`调整主题
2. 更新`gui/components/`添加新组件
3. 配置`config.json`保存用户偏好

## 性能优化

### 代码生成优化
- 使用结构化Prompt减少LLM幻觉
- 知识库检索提高参数准确性
- 流式输出提升用户体验

### 执行环境优化
- 预加载常用库减少启动时间
- 缓存频繁查询的数据
- 异步执行长时间运行的任务

## 安全考虑

### 代码执行安全
- 沙箱环境执行用户生成的代码
- 限制文件系统访问权限
- 过滤危险系统调用

### 数据安全
- Token加密存储
- API调用频率限制
- 敏感数据脱敏处理
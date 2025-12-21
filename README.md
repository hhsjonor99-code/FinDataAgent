# FinDataAgent · 智能金融数据助手（DeepSeek + Tushare + Streamlit）

## 项目简介
FinDataAgent 是一个通过自然语言驱动的金融数据分析助手。系统采用“代码解释器（Code Interpreter）”工作流：LLM 根据用户意图自动编写 Python 代码，系统注入必要的依赖与上下文后执行脚本，输出数据文件与图表。界面基于 Streamlit 构建，提供聊天式交互与进度/结果展示。

## 核心特性
- 自然语言分析：输入需求即可获取数据、导出 Excel、绘制折线图。
- 自动代码生成与执行：LLM 生成完整 Python 脚本，系统安全执行并捕获输出。
- 轻量知识库增强：内置 Tushare 接口 Schema，降低参数错误风险。
- 现代化界面：聊天气泡、渐变背景、个性化设置。

## 技术栈
- `LLM`：DeepSeek（OpenAI 兼容 API）
- `Data`：Tushare Pro
- `GUI`：Streamlit
- `Runtime`：Python 3.13（见 `.python-version`）
- `包管理`：`uv`

## 架构概览
- `核心引擎`：`core/agent_engine.py` 实现主工作流与流式工作流
  - 主流程：`agent_workflow(intent)` `core/agent_engine.py:28`
  - 流式输出：`agent_workflow_streaming(intent)` `core/agent_engine.py:127`
- `代码执行器`：`tools/code_executor.py` 注入前置依赖并执行脚本（Matplotlib 无交互后端、Tushare Token 初始化等）`tools/code_executor.py:1`
- `知识库`：`knowledge_base/tushare_schema.json` 作为接口参考手册 `knowledge_base/tushare_schema.json:1`
- `检索适配`：`core/knowledge_manager.py` 聚合知识文本供 Prompt 使用 `core/knowledge_manager.py:1`
- `GUI`：`gui/app.py` 页面编排；`components/*` 组件化渲染；`styles/theme.py` 注入主题与 CSS `gui/app.py:28` `gui/styles/theme.py:67`

## 目录结构
- `core/` 智能体工作流与日志
- `tools/` 脚本执行与绘图库初始化
- `knowledge_base/` 轻量接口文档（Schema）
- `gui/` Streamlit 前端（聊天、进度、结果卡片、主题）
- `workspace/` 输出目录（导出文件与临时脚本）
- `start_app.bat` Windows 启动脚本（使用 `uv run`）
- `requirements.txt` 与 `pyproject.toml` 依赖声明

## 快速开始
1) 准备环境

- 使用 `uv` 安装所需依赖：
  - 安装 `uv`（`pip install uv`）
  - 运行命令 uv sync
  

2) 配置密钥（在项目根目录创建 `.env`）
- `TUSHARE_TOKEN=你的Tushare密钥`
- `DEEPSEEK_API_KEY=你的DeepSeek密钥`
- 可选：`DEEPSEEK_BASE_URL=https://api.deepseek.com/v1`
- 可选：`DEEPSEEK_MODEL=deepseek-chat`

3) 运行界面
- 双击 `start_app.bat` 
- 或者 `uv run streamlit run gui/app.py`

## 运行与测试
- GUI 启动后，输入如“分析茅台近一年的股价趋势”，观察思考流与结果卡片。
- 文件输出位于 `workspace/exports/`；侧边栏提供“打开输出文件夹”按钮 `gui/app.py:37`。
- 命令行测试：运行 `python min_test.py` 验证绘图与导出流程 `min_test.py:1`。

## 配置与持久化
- 主题与头像保存在 `config.json`，由 `gui/services/config_manager.py` 读写 `gui/services/config_manager.py:1`。
- 日志输出保存在 `core/agent_log_record/agent.log`，前端可读取并展示 `gui/components/chat.py:52`。
- 代码执行器自动创建 `workspace/exports/` 与 `workspace/temp_scripts/` 并打印 `OUTPUT_PATH:` 便于 UI 捕获 `tools/code_executor.py:29` `tools/code_executor.py:39`。

## 示例指令
- “获取贵州茅台近365日收盘价并绘制折线图”
- “导出600519.SH在2023-01-01至2023-01-31的日线到Excel”
- “获取中国GDP季度数据从2018Q1到2019Q3，仅选择quarter,gdp,gdp_yoy并导出Excel”

## 注意事项
- 首次运行请确保 `.env` 已配置有效的 `TUSHARE_TOKEN` 与 `DEEPSEEK_API_KEY`。
- 若浏览器未自动打开，手动访问本地地址（Streamlit 默认 `http://localhost:8501/`）。
- 当前实现以折线图与Excel导出为主，更多图表类型可在 `knowledge_base/` 扩充后由 LLM 自适应生成。

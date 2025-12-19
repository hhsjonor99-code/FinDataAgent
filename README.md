# FinDataAgent: 基于 DeepSeek 的智能金融数据助手

## 项目简介：
本项目是《软件过程与项目管理》课程作业。通过集成 DeepSeek 大模型、LangChain 框架与 Tushare 财经数据接口，实现了一个能够通过自然语言指令自动获取金融数据、生成分析报表并绘制统计图表的 AI Agent。

## 核心特性：
自然语言交互：无需编写代码，通过对话即可完成数据抓取。
自动代码生成：Agent 根据需求检索 API 文档并生成 Python 执行脚本。
本地知识库：内置 Tushare API Schema，确保接口调用的准确性。
可视化输出：自动生成 Excel 报表与 Matplotlib 折线图。

## 技术栈：
LLM: DeepSeek-V3 (OpenAI 兼容接口)
Orchestration: LangChain
Data Source: Tushare Pro
GUI: Python Tkinter

## 数据流：
用户意图 -> 知识检索 -> 代码生成 -> 外部调用 -> 结果固化

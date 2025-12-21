# FinDataAgent GUI 可视化重构方案（Streamlit）

## 设计目标

- 对话式布局：主区域采用与 DeepSeek 相似的聊天气泡与底部输入框，左侧为对话，右侧为进度与结果概览。
- 高度解耦：UI 布局与后端回调完全隔离，通过事件适配层与状态存储交互。
- 现代化视觉：在大块留白处使用高透明度、低饱和度的暖色渐变背景，玻璃化卡片、柔和阴影，无异常白边。
- 技术栈与范围：仅改动 `gui` 模块，使用 Streamlit 原生能力与少量 CSS。

## 信息架构

- 顶栏（标题/操作）：展示产品名与轻量操作入口（帮助、设置）。
- 主对话区（聊天）：用户与助手消息气泡，支持文件预览与轻量分栏渲染。
- 思考块（提交态）：在提交期间实时展示思考、执行、错误、结果的阶段进度与内容。
- 结果展示块（实时渲染）：对图片、表格、可下载文件进行卡片化预览与下载。
- 右侧信息区：展现整体进度条（阶段进度）、事件时间线。
- 侧边栏：工作区入口按钮，可直接打开 `workspace/exports` 文件夹。

## 模块划分（仅在 gui/ 下新增文件/目录）

- `app.py`：页面编排入口，路由/控制器。
- `components/`
  - `topbar.py`：标题与操作按钮。
  - `chat.py`：消息渲染与输入框。
  - `thinking.py`：提交时的思考块（状态/进度）。
  - `results.py`：结果卡片与预览下载。
  - `timeline.py`：事件时间线。
- `services/`
  - `agent_stream.py`：封装后端流式接口，输出统一 UI 事件。
  - `events.py`：事件类型、适配与进度映射（仅处理数据，不含 UI）。
- `state/`
  - `store.py`：集中管理 `session_state`，暴露只读选择器与更新方法。
- `styles/`
  - `theme.py` 或 `styles.css`：统一注入暖色渐变与气泡样式，隐藏默认页眉/页脚，修正白边。

说明：如不希望增加文件数量，可保持在 `app.py` 内逐步内聚为模块函数，但推荐上面目录以实现清晰解耦。

## 与后端的解耦设计

- 事件协议：约定后端流（JSON 行）包含 `type`（`thought`/`thought_stream`/`execution`/`error`/`result`）、`content`、`data`、`success`。
- 适配层：`services/events.py` 中实现 `adapt_event(raw)`，将后端事件映射为 UI 事件：`stage`（`plan`/`run`/`done`）、`progress`（0.0–1.0）、`attachments`（解析文件路径）。
- 数据流：
  - `components/chat.py` 仅调用 `services/agent_stream.run(prompt)` 获取事件迭代器；
  - 每个事件交给 `state/store.py` 更新集中状态；
  - `thinking.py`/`results.py`/`timeline.py` 通过只读选择器渲染，不直接接触后端数据结构。
- 错误隔离：后端异常作为 `error` 事件进入时间线；UI 不因解析失败而中断，保证界面稳定。

## 交互流程（与 DeepSeek 相似）

- 用户输入提交 → 生成一条用户气泡。
- 启动思考块：显示 `🤔 思考`、`⌛ 执行`、`✅ 完成` 阶段进度。
- 流式事件：
  - `thought`/`thought_stream` → 思考块顶部实时文本；
  - `execution` → 代码/操作片段以代码块呈现；
  - `error` → 红色警示行进入时间线；
  - `result` → 最终结果文本与附件解析，推送到结果展示块并追加助手气泡。
- 右侧信息区：随事件更新进度条与时间线。

## 组件细节（满足你的 6 个组件需求）

- 对话框（Chat）：`st.chat_message` 渲染气泡，`st.chat_input` 固定悬浮输入框，支持多行。
- 标题（Title）：顶栏 `📊 FinDataAgent` 与版本/轻量操作。
- 使用说明（Tips）：侧边栏简短引导与预设按钮（如“分析某股价趋势”）。
- 思考块（Thinking）：使用 `st.status` 或自定义容器，分阶段展示思考/执行/错误；在移动端保持收敛高度。
- 实时结果展示（Results）：图片 `st.image`；表格 `st.dataframe`；下载 `st.download_button`；卡片化与懒加载预览。
- 打开工作区按钮（Open Workspace）：跨平台 `open_folder(path)`，悬浮提示与失败告警。

## 视觉与主题（避免异常白边）

- 背景：`linear-gradient(180deg, #fdfbf7 0%, #fff5eb 100%)`，固定与响应式适配。
- 容器：限制 `.block-container` 最大宽度（约 1100px），移除默认页眉/页脚与主菜单；底部为输入框预留空间。
- 气泡：玻璃化背景（`rgba(255,255,255,0.9)`）、圆角、柔和阴影；用户气泡左侧加入暖色强调边线。
- 输入框：居中悬浮、胶囊形边框、轻阴影，避免遮挡与边缘溢出。
- 移动端：缩小底部间距、左右内边距一致，确保无突兀白边。
- 可访问性：颜色对比度符合 WCAG AA，提示与错误信息明显但不刺眼。

## 文件结构建议（落地示例）

```
gui/
  app.py
  components/
    topbar.py
    chat.py
    thinking.py
    results.py
    timeline.py
  services/
    agent_stream.py
    events.py
  state/
    store.py
  styles/
    theme.py
    styles.css
```

上述目录均在 `gui` 内创建，确保不影响其他模块。

## 渐进式重构步骤（建议里程碑）

- M1：抽离事件适配层
  - 将 `app.py` 中的 `adapt_event` 移至 `services/events.py`，补充类型与进度映射。
- M2：集中状态管理
  - 在 `state/store.py` 统一初始化/读写 `session_state`，组件仅读状态。
- M3：组件化布局
  - 拆分顶栏、聊天、思考块、结果、时间线为独立渲染函数，`app.py` 负责编排。
- M4：主题与样式
  - 将 CSS 注入逻辑移动到 `styles/theme.py`（或单独 `styles.css`），统一维护视觉规范。
- M5：文件预览能力
  - 完善图片/表格/下载的卡片展示与懒预览，容错与提示完善。
- M6：端到端测试
  - 在 Windows/Chrome 上检查无异常白边、移动端适配、工作区按钮可用。

## 验收标准（无异常白边的检查清单）

- 页面无默认页眉/页脚；容器左右留白与内容对齐，无不规则白边。
- 输入框固定于底部居中，不遮挡对话内容，无溢出。
- 渐变背景在不同分辨率下连续且无色带；滚动无闪烁。
- 思考块在流式事件下稳定更新，不跳动高度；错误信息样式一致。
- 结果卡片预览与下载均可用；不存在空卡片或断链。
- 打开工作区按钮在 Windows/macOS/Linux 均可工作或给出友好提示。

## 运行与测试

- 命令：`streamlit run gui/app.py`
- 测试建议：
  - 输入“分析茅台近一年的股价趋势”，观察思考块与进度更新；
  - 触发生成文件后，结果卡片应实时出现；
  - 点击侧边栏按钮打开 `workspace/exports` 并校验路径；
  - 在移动端/窄屏检查是否存在异常白边与遮挡。

## 参考（当前实现位置，便于对照）

- 自定义 CSS 与暖色渐变：`gui/app.py:24-121`
- 事件适配与进度映射：`gui/app.py:191-223`
- 工作区按钮与文件夹打开：`gui/app.py:165-183`, `gui/app.py:144-155`
- 思考块与流式处理：`gui/app.py:326-410`
- 结果卡片与预览下载：`gui/app.py:225-269`, `gui/app.py:397-407`

本方案在现有基础上增强解耦与一致性，并可分阶段落地，确保只改动 `gui` 模块与 Streamlit 技术栈，最终达到与 DeepSeek 类似的对话式体验与现代化视觉呈现。

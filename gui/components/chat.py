import json
import os
import streamlit as st
from state import store
from services.agent_stream import stream_agent
from services.events import adapt_event

 

def render_messages():
    for msg in store.get_messages():
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

import re

def parse_log_lines(lines):
    parsed_logs = []
    for line in lines:
        # Regex to match standard logging format
        # 2025-12-20 15:24:38,862 INFO agent ...
        match = re.match(r'(\d{4}-\d{2}-\d{2}\s+(\d{2}:\d{2}:\d{2})),\d+\s+(\w+)\s+(\w+)\s+(.*)', line)
        if match:
            _, time_str, level, module, content = match.groups()
            
            # Icon based on level
            icon = "📝"
            if level == "INFO": icon = "ℹ️"
            elif level == "WARNING": icon = "⚠️"
            elif level == "ERROR": icon = "❌"
            elif level == "DEBUG": icon = "🐛"
            
            # Try to format JSON content
            try:
                if content.strip().startswith('{') and content.strip().endswith('}'):
                    # Just keep it as one line to save space, or partial format
                    pass
            except:
                pass
                
            parsed_logs.append(f"{time_str} {icon} [{module}] {content}")
        else:
            parsed_logs.append(line.strip())
    return "\n".join(parsed_logs)

def get_log_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core', 'agent_log_record', 'agent.log'))

def read_formatted_logs(max_lines: int = 20):
    try:
        log_path = get_log_path()
        if not os.path.exists(log_path):
            return ""
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-max_lines:]
        return parse_log_lines(lines)
    except Exception:
        return ""

def render_agent_status(status_container, events, logs_only=False):
    """
    Utility to render status from events list.
    Used for restoring state after rerun.
    """
    if not events and not logs_only:
        return

    with status_container:
        thought_placeholder = st.empty()
        code_placeholder = st.empty()
        log_placeholder = st.empty()

        # Replay events to find latest state
        latest_thought = ""
        latest_code = ""
        
        for ev in events:
            t = ev.get('type')
            c = ev.get('content', '')
            if t == 'thought':
                latest_thought = f"### :material/psychology: 思考中...\n{c}"
            elif t == 'execution':
                latest_thought = f"### :material/terminal: 执行代码\n正在执行 Python 代码..."
                latest_code = c
            elif t == 'error':
                latest_thought = f"### :material/error: 发生错误\n{c}"

        if latest_thought:
            thought_placeholder.markdown(latest_thought)
        if latest_code:
            code_placeholder.code(latest_code, language="python")
        
        # Always show logs
        logs = read_formatted_logs()
        if logs:
            log_placeholder.code(logs, language="text")

def process_response(prompt: str):
    # Clear previous events for new run
    store.clear_events()
    
    full_response = ""
    status_container = st.status("Agent 正在分析数据...", expanded=True)
    
    # 使用占位符防止内容无限堆叠
    with status_container:
        thought_placeholder = st.empty()
        code_placeholder = st.empty()
        log_placeholder = st.empty()
    
    store.set_running(True)
    store.set_stop(False)
    
    try:
        stream = stream_agent(prompt)
        
        for output in stream:
            if store.get_stop():
                store.append_event({'type': 'cancelled', 'stage': 'stop', 'progress': 1.0, 'content': '已取消', 'success': False, 'attachments': []})
                status_container.update(label=":material/stop_circle: 已取消", state="error", expanded=False)
                full_response = "任务已取消"
                break
            for line in output.split('\n'):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    msg_type = data.get('type')
                    content = data.get('content', '')
                    result_data = data.get('data', '')
                    ev = adapt_event(data)
                    store.append_event(ev)
                    
                    # 更新日志
                    logs = read_formatted_logs()
                    if logs:
                        log_placeholder.code(logs, language="text")

                    if msg_type == 'thought':
                        thought_placeholder.markdown(f"### :material/psychology: 思考中...\n{content}")
                        status_container.update(label=f":material/sync: {ev.get('stage', '处理中')} ({int(ev.get('progress',0)*100)}%)")
                        
                    elif msg_type == 'thought_stream':
                        # 如果需要流式更新思考内容，可以在这里处理
                        pass
                        
                    elif msg_type == 'execution':
                        thought_placeholder.markdown(f"### :material/terminal: 执行代码\n正在执行 Python 代码...")
                        code_placeholder.code(content, language="python")
                        status_container.update(label=f":material/terminal: 执行代码 ({int(ev.get('progress',0)*100)}%)")
                        
                    elif msg_type == 'error':
                        thought_placeholder.markdown(f"### :material/error: 发生错误\n{content}")
                        status_container.update(label=":material/error: 出错了", state="error")
                        
                    elif msg_type == 'result':
                        if data.get('success'):
                            full_response = result_data
                            status_container.update(label=":material/check_circle: 分析完成", state="complete", expanded=False)
                            # 任务完成后，保留最后的日志在 status 中
                            thought_placeholder.empty()
                            code_placeholder.empty()
                            # 最终结果显示在 status 外部，或者在 status 内部最后更新
                            status_container.write(full_response)
                        else:
                            full_response = f"⚠️ 任务失败: {result_data}"
                            status_container.update(label=":material/cancel: 任务中止", state="error")
                            status_container.write(full_response)
                            
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        status_container.update(label=":material/error: 系统异常", state="error")
        full_response = f"系统错误: {str(e)}"
        status_container.write(full_response)
    
    store.set_running(False)
    return full_response

def render():
    render_messages()
    
    # Restore interrupted or ongoing status
    events = store.get_events()
    if events and store.is_running():
        # This implies an interruption happened (script rerun while running)
        store.set_running(False)
        store.append_event({'type': 'error', 'content': '任务因页面刷新或操作而中断', 'stage': 'Interrupted'})
        
        with st.chat_message("assistant"):
             status_container = st.status(":material/error: 任务中断", expanded=True, state="error")
             render_agent_status(status_container, events)
             st.error("任务似乎被中断了。请重试。")

    prompt = st.chat_input("请输入您的数据分析需求...")
    if prompt:

        if store.is_running():
            st.toast("当前有任务正在进行", icon=":material/hourglass_top:")
        else:
            store.append_message({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                response_text = process_response(prompt)
                store.append_message({
                    "role": "assistant",
                    "content": response_text
                })

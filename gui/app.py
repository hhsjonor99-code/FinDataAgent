import streamlit as st
import sys
import os
import json
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# 将项目根目录添加到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent_engine import agent_workflow

st.title("FinDataAgent")

# 初始化session_state
if 'thinking_process' not in st.session_state:
    st.session_state.thinking_process = ""
if 'final_result' not in st.session_state:
    st.session_state.final_result = ""
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""

# 需求输入框
user_input = st.text_area("请输入您的数据分析需求：", height=150)

if st.button("开始分析"):
    if user_input:
        st.session_state.thinking_process = ""
        st.session_state.final_result = ""
        st.session_state.error_message = ""

        # AI思考展示框
        thinking_placeholder = st.empty()
        
        try:
            for output in agent_workflow(user_input):
                data = json.loads(output)
                
                if data['type'] == 'thought' or data['type'] == 'execution' or data['type'] == 'error':
                    st.session_state.thinking_process += f"> {data['content']}\n\n"
                elif data['type'] == 'thought_stream':
                    st.session_state.thinking_process += data['content']
                
                thinking_placeholder.markdown(f"**AI 思考中...**\n```\n{st.session_state.thinking_process}\n```")

                if data['type'] == 'result':
                    if data['success']:
                        st.session_state.final_result = data['data']
                    else:
                        st.session_state.error_message = data['data']

        except Exception as e:
            st.session_state.error_message = f"An unexpected error occurred: {str(e)}"

    else:
        st.warning("请输入您的需求。")

# AI提示框
if st.session_state.final_result:
    st.success(st.session_state.final_result)

if st.session_state.error_message:
    st.error(f"分析失败: {st.session_state.error_message}")
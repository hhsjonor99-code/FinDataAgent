import streamlit as st
import sys
import os
import platform
import subprocess
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from styles.theme import apply_theme
from state import store
from components.topbar import render as render_topbar
from components.chat import render as render_chat
 

def open_folder(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        st.error(f"无法打开文件夹: {e}")

def render_sidebar():
    with st.sidebar:
        st.markdown("# :material/analytics: FinData Agent")
        st.caption("v1.1 | 数据获取与可视化分析助手")
        if st.button("设置", width='stretch', icon=":material/settings:"):
            st.toast("设置功能开发中", icon=":material/build:")
        
        st.markdown("### :material/work: 工作区")
        workspace_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace', 'exports'))
        
        if st.button("打开输出文件夹", width='stretch', icon=":material/folder_open:"):
            if os.path.exists(workspace_path):
                open_folder(workspace_path)
                st.toast("文件夹已打开", icon=":material/check_circle:")
            else:
                st.warning("文件夹尚未创建")
                
        st.divider()
        st.info("示例: 获取贵州茅台近365日收盘价, 绘制折线图, 并将CSV导出到 workspace/exports", icon=":material/lightbulb:")
        
        if store.is_running():
            if st.button("停止运行", type="secondary", width='stretch', icon=":material/stop_circle:"):
                store.request_stop()
                st.toast("已请求停止", icon=":material/stop_circle:")

def main():
    load_dotenv()
    apply_theme()
    store.init()
    render_topbar()
    render_sidebar()
    render_chat()

if __name__ == "__main__":
    main()

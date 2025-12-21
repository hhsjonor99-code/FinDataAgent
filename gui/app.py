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
from services.config_manager import set_theme, get_theme, set_user_avatar, set_agent_avatar, get_avatars, get_llm_model, set_llm_model
from styles.theme import THEMES

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
        
        st.divider()
        
        # 1. 工作区 (Workspace)
        st.markdown("### :material/work: 工作区")
        workspace_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace', 'exports'))
        
        if st.button("打开输出文件夹", width='stretch', icon=":material/folder_open:"):
            if os.path.exists(workspace_path):
                open_folder(workspace_path)
                st.toast("文件夹已打开", icon=":material/check_circle:")
            else:
                st.warning("文件夹尚未创建")
        
        # 2. 示例 (Examples)
        st.divider()
        st.info("示例: 获取贵州茅台近365日收盘价, 并绘制折线图", icon=":material/lightbulb:")
        
        # 3. 设置 (Settings)
        st.divider()
        with st.expander("⚙️ 设置", expanded=False):
            # Theme Settings
            st.caption("界面风格")
            current_theme = get_theme()
            theme_names = list(THEMES.keys())
            
            try:
                current_index = theme_names.index(current_theme)
            except ValueError:
                current_index = 0
                
            selected_theme = st.selectbox(
                "主题皮肤", 
                theme_names, 
                index=current_index,
                key="theme_selector"
            )
            
            if selected_theme != current_theme:
                set_theme(selected_theme)
                st.toast(f"已切换为 {selected_theme}", icon="🎨")
                # 强制重新运行以立即生效
                st.rerun()
            
            st.divider()
            
            # Avatar Settings
            st.caption("角色图标")
            avatars = get_avatars()
            
            user_options = ["👤", "👨‍💻", "👩‍💻", "🎓", "🚀", "🐱", "🐶", "⭐", "💠"]
            agent_options = ["🤖", "🧠", "⚡", "🔮", "🧬", "🦉", "🐳", "🎓", "🦁"]
            
            # User Avatar
            try:
                user_index = user_options.index(avatars["user"])
            except ValueError:
                user_index = 0
                
            selected_user = st.selectbox(
                "用户图标",
                user_options,
                index=user_index,
                key="user_avatar_selector"
            )
            
            if selected_user != avatars["user"]:
                set_user_avatar(selected_user)
                st.toast("用户图标已更新", icon="👤")
                st.rerun()
                
            # Agent Avatar
            try:
                agent_index = agent_options.index(avatars["agent"])
            except ValueError:
                agent_index = 0
                
            selected_agent = st.selectbox(
                "智能体图标",
                agent_options,
                index=agent_index,
                key="agent_avatar_selector"
            )
            
            if selected_agent != avatars["agent"]:
                set_agent_avatar(selected_agent)
                st.toast("智能体图标已更新", icon="🤖")
                st.rerun()

            st.divider()
            
            st.caption("模型配置")
            models = ["deepseek-chat", "deepseek-reasoner"]
            current_model = get_llm_model()
            try:
                model_index = models.index(current_model)
            except ValueError:
                model_index = 0
            selected_model = st.selectbox(
                "LLM模型",
                models,
                index=model_index,
                key="llm_model_selector"
            )
            if selected_model != current_model:
                set_llm_model(selected_model)
                st.toast("LLM模型已更新", icon="🧠")
                st.rerun()
        
        if store.is_running():
            st.divider()
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

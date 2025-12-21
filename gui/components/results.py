import os
import pandas as pd
import streamlit as st
from state import store

def render_file_card(file_path: str):
    if not os.path.exists(file_path):
        return
    filename = os.path.basename(file_path)
    ext = filename.split('.')[-1].lower()
    with st.container():
        st.markdown(f"""
        <div class="file-card">
            <span style="font-size: 20px;">📄</span>
            <div>
                <strong>{filename}</strong><br>
                <span style="color: #666; font-size: 0.8em;">{ext.upper()} 文件</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if ext == 'png':
            st.image(file_path, caption=filename, width='stretch')
        elif ext in ['xlsx', 'csv']:
            with st.expander(f"预览数据: {filename}"):
                try:
                    if ext == 'xlsx':
                        df = pd.read_excel(file_path)
                    else:
                        df = pd.read_csv(file_path)
                    st.dataframe(df.head(10), width='stretch')
                except Exception as e:
                    st.warning(f"无法预览: {e}")
        with open(file_path, 'rb') as f:
            st.download_button("下载", f.read(), file_name=filename, key=f"download-{os.path.abspath(file_path)}", width='stretch')

def render_outputs_panel():
    files = store.get_generated_files()
    if files:
        st.markdown("### 📂 生成结果")
        cols = st.columns(3)
        for i, p in enumerate(files):
            with cols[i % 3]:
                render_file_card(p)

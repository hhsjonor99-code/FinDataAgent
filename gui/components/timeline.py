import streamlit as st
from state import store

def render_progress_panel():
    evs = store.get_events()
    if not evs:
        return
    last = evs[-1]
    p = float(last.get('progress', 0))
    st.progress(p)
    st.caption(f"阶段: {last.get('stage', '')}")

def render_event_timeline(max_items: int = 50):
    evs = store.get_events()
    if not evs:
        return
    st.markdown("### ⏱️ 事件进度")
    for e in evs[-max_items:]:
        t = e.get('type')
        c = e.get('content', '')
        if t == 'error':
            st.error(c)
        elif t == 'execution':
            st.code(c)
        elif t == 'thought_stream':
            st.write(c)
        elif t == 'thought':
            st.write(c)
        elif t == 'cancelled':
            st.warning(c)

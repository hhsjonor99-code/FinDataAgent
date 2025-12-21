import streamlit as st

def init():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'generated_files_all' not in st.session_state:
        st.session_state.generated_files_all = []
    if 'events' not in st.session_state:
        st.session_state.events = []
    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'stop' not in st.session_state:
        st.session_state.stop = False

def get_messages():
    return st.session_state.get('messages', [])

def append_message(msg):
    st.session_state.messages.append(msg)

def get_events():
    return st.session_state.get('events', [])

def append_event(ev):
    st.session_state.events.append(ev)

def clear_events():
    st.session_state.events = []

def get_generated_files():
    return st.session_state.get('generated_files_all', [])

def add_generated_file(path):
    if path not in st.session_state.generated_files_all:
        st.session_state.generated_files_all.append(path)

def is_running():
    return bool(st.session_state.get('running'))

def set_running(val: bool):
    st.session_state.running = bool(val)

def get_stop():
    return bool(st.session_state.get('stop'))

def set_stop(val: bool):
    st.session_state.stop = bool(val)

def request_stop():
    st.session_state.stop = True

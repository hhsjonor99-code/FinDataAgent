import streamlit as st

PAGE_TITLE = "FinDataAgent"
PAGE_ICON = "📊"
LAYOUT = "wide"

CSS = """
<style>
    :root {
        --primary-color: #FF6B6B;
        --accent-color: #2EC4B6;
        /* More refined warm gradient palette */
        --bg-gradient-start: #fff8f5;  /* Very pale warm white */
        --bg-gradient-end: #ffe4d6;    /* Soft peach */
        --overlay-start: rgba(255, 209, 179, 0.25); /* Light coral, low opacity */
        --overlay-end: rgba(255, 196, 196, 0.35);   /* Soft rose, low opacity */
        --glass-bg: rgba(255, 250, 245, 0.92);
        --glass-border: 1px solid rgba(255, 180, 150, 0.30);
        --card-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
        --input-bg: rgba(255, 245, 240, 0.92);
    }
    .stApp {
        background:
            radial-gradient(circle at 10% 20%, var(--overlay-start) 0%, transparent 50%),
            radial-gradient(circle at 90% 80%, var(--overlay-end) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.8) 0%, transparent 50%),
            linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
        background-size: 200% 200%;
        background-attachment: scroll;
        animation: gradientFlow 15s ease infinite alternate;
        min-height: 100vh;
    }
    .stApp::after { display: none !important; }
    html, body {
        background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%) !important;
        margin: 0 !important;
    }
    [data-testid="stAppViewContainer"] { background: transparent !important; }
    section.main { background: transparent !important; }
    #root { background: transparent !important; }
    @keyframes gradientFlow {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
    }
    .block-container {
        max-width: 1100px !important;
        padding-top: 2rem !important;
        padding-bottom: 120px !important; /* Increased padding to accommodate higher input box */
        margin: 0 auto !important;
        background: transparent !important;
    }
    .stChatMessage {
        background-color: var(--glass-bg);
        border: var(--glass-border);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }
    [data-testid="stChatMessage"][data-test-role="user"] {
        background-color: rgba(255, 240, 235, 0.8);
        border-left: 4px solid var(--primary-color);
    }
    [data-testid="stBottom"] {
        background: transparent !important;
        background-color: transparent !important;
        border-top: none !important;
        box-shadow: none !important;
    }
    [data-testid="stBottom"] > div {
        background: transparent !important;
    }
    .stChatInput {
        position: fixed;
        bottom: 80px; /* Moved up from 56px */
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 800px;
        z-index: 1000;
        padding: 0 1rem;
    }
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background: var(--input-bg) !important;
        box-shadow: none !important;
        border: none !important;
        outline: none !important;
    }
    [data-testid="stChatInput"] textarea {
        height: auto !important;
        min-height: 24px !important;
        padding: 12px !important;
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    .file-card {
        background: white;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #eee;
        margin-top: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    footer {display: none !important;}
    header {background: transparent !important;}
    @media (max-width: 600px) {
        .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .stChatInput {
            bottom: 10px;
        }
    }
</style>
"""

def apply_theme():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="auto"
    )
    # Inject Material Symbols font for custom HTML components
    st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
    st.markdown(CSS, unsafe_allow_html=True)

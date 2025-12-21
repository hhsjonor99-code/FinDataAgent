import streamlit as st
from gui.services.config_manager import get_theme

PAGE_TITLE = "FinDataAgent"
PAGE_ICON = "📊"
LAYOUT = "wide"

THEMES = {
    "Warm Peach": {
        "primary-color": "#FF6B6B",
        "accent-color": "#2EC4B6",
        "bg-gradient-start": "#fff8f5",
        "bg-gradient-end": "#ffe4d6",
        "overlay-start": "rgba(255, 160, 122, 0.4)",
        "overlay-end": "rgba(255, 127, 80, 0.5)",
        "glass-bg": "rgba(255, 250, 245, 0.92)",
        "glass-border": "1px solid rgba(255, 180, 150, 0.30)",
        "card-shadow": "0 6px 20px rgba(0, 0, 0, 0.06)",
        "input-bg": "rgba(255, 245, 240, 0.92)",
        "sidebar-bg": "rgba(255, 230, 220, 0.05)",
        "sidebar-accent": "rgba(255, 107, 107, 0.08)"
    },
    "Ocean Blue": {
        "primary-color": "#4A90E2",
        "accent-color": "#50E3C2",
        "bg-gradient-start": "#f0f8ff",
        "bg-gradient-end": "#e6f2ff",
        "overlay-start": "rgba(74, 144, 226, 0.25)",
        "overlay-end": "rgba(80, 227, 194, 0.35)",
        "glass-bg": "rgba(245, 250, 255, 0.92)",
        "glass-border": "1px solid rgba(74, 144, 226, 0.20)",
        "card-shadow": "0 6px 20px rgba(0, 0, 0, 0.06)",
        "input-bg": "rgba(240, 248, 255, 0.92)",
        "sidebar-bg": "rgba(230, 245, 255, 0.05)",
        "sidebar-accent": "rgba(74, 144, 226, 0.08)"
    },
    "Mint Fresh": {
        "primary-color": "#2ECC71",
        "accent-color": "#27AE60",
        "bg-gradient-start": "#f5fff5",
        "bg-gradient-end": "#e8f8f5",
        "overlay-start": "rgba(46, 204, 113, 0.25)",
        "overlay-end": "rgba(39, 174, 96, 0.35)",
        "glass-bg": "rgba(250, 255, 250, 0.92)",
        "glass-border": "1px solid rgba(46, 204, 113, 0.20)",
        "card-shadow": "0 6px 20px rgba(0, 0, 0, 0.06)",
        "input-bg": "rgba(245, 255, 245, 0.92)",
        "sidebar-bg": "rgba(235, 255, 240, 0.05)",
        "sidebar-accent": "rgba(46, 204, 113, 0.08)"
    },
    "Lavender Dream": {
        "primary-color": "#9B59B6",
        "accent-color": "#8E44AD",
        "bg-gradient-start": "#faf5ff",
        "bg-gradient-end": "#f3e5f5",
        "overlay-start": "rgba(155, 89, 182, 0.25)",
        "overlay-end": "rgba(142, 68, 173, 0.35)",
        "glass-bg": "rgba(252, 245, 255, 0.92)",
        "glass-border": "1px solid rgba(155, 89, 182, 0.20)",
        "card-shadow": "0 6px 20px rgba(0, 0, 0, 0.06)",
        "input-bg": "rgba(250, 240, 255, 0.92)",
        "sidebar-bg": "rgba(245, 235, 255, 0.05)",
        "sidebar-accent": "rgba(155, 89, 182, 0.08)"
    }
}

def get_css(theme_name):
    theme = THEMES.get(theme_name, THEMES["Warm Peach"])
    
    return f"""
<style>
    :root {{
        --primary-color: {theme["primary-color"]};
        --accent-color: {theme["accent-color"]};
        --bg-gradient-start: {theme["bg-gradient-start"]};
        --bg-gradient-end: {theme["bg-gradient-end"]};
        --overlay-start: {theme["overlay-start"]};
        --overlay-end: {theme["overlay-end"]};
        --glass-bg: {theme["glass-bg"]};
        --glass-border: {theme["glass-border"]};
        --card-shadow: {theme["card-shadow"]};
        --input-bg: {theme["input-bg"]};
        --sidebar-bg: {theme.get("sidebar-bg", "rgba(255, 255, 255, 0.05)")};
        --sidebar-accent: {theme.get("sidebar-accent", "rgba(0, 0, 0, 0.05)")};
    }}
    .stApp {{
        background:
            radial-gradient(circle at 10% 20%, var(--overlay-start) 0%, transparent 60%),
            radial-gradient(circle at 90% 80%, var(--overlay-end) 0%, transparent 60%),
            radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.8) 0%, transparent 50%),
            linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
        background-size: 200% 200%;
        background-attachment: scroll;
        animation: gradientFlow 8s ease infinite alternate;
        min-height: 100vh;
    }}
    .stApp::after {{ display: none !important; }}
    html, body {{
        background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%) !important;
        margin: 0 !important;
    }}
    [data-testid="stAppViewContainer"] {{ background: transparent !important; }}
    section.main {{ background: transparent !important; }}
    #root {{ background: transparent !important; }}
    @keyframes gradientFlow {{
        0% {{ background-position: 0% 0%; }}
        100% {{ background-position: 100% 100%; }}
    }}
    .block-container {{
        max-width: 1100px !important;
        padding-top: 2rem !important;
        padding-bottom: 120px !important;
        margin: 0 auto !important;
        background: transparent !important;
    }}
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: transparent !important;
        border-right: 1px solid var(--glass-border);
    }}
    
    [data-testid="stSidebar"] .stButton button {{
        background-color: var(--sidebar-bg);
        border: 1px solid var(--glass-border);
        color: #444;
        transition: all 0.3s ease;
    }}
    
    [data-testid="stSidebar"] .stButton button:hover {{
        background-color: var(--sidebar-accent);
        border-color: var(--primary-color);
        color: var(--primary-color);
        transform: translateY(-1px);
    }}
    
    [data-testid="stSidebar"] [data-testid="stExpander"] {{
        background-color: var(--sidebar-bg);
        border: 1px solid var(--glass-border);
        border-radius: 8px;
    }}
    
    [data-testid="stSidebar"] .stAlert {{
        background-color: transparent !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        color: #444 !important;
    }}
    [data-testid="stSidebar"] [role="alert"],
    [data-testid="stSidebar"] [data-testid="stAlert"],
    [data-testid="stSidebar"] .stAlert > div,
    [data-testid="stSidebar"] .stAlert div {{
        background-color: transparent !important;
        box-shadow: none !important;
    }}

    [data-testid="stSidebar"] .stAlert [data-testid="stMarkdownContainer"] {{
        color: #444 !important;
    }}
    
    [data-testid="stSidebar"] .stAlert svg {{
        fill: #444 !important;
        color: #444 !important;
    }}
    
    [data-testid="stSidebar"] hr {{
        border-color: var(--glass-border) !important;
        opacity: 0.5;
    }}

    .stChatMessage {{
        background-color: var(--glass-bg);
        border: var(--glass-border);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }}
    [data-testid="stChatMessage"][data-test-role="user"] {{
        background-color: rgba(255, 255, 255, 0.5); /* Generalized user bubble */
        border-left: 4px solid var(--primary-color);
    }}
    [data-testid="stBottom"] {{
        background: transparent !important;
        background-color: transparent !important;
        border-top: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stBottom"] > div {{
        background: transparent !important;
    }}
    .stChatInput {{
        position: static !important;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    }}
    [data-testid="stChatInput"] {{
        border-radius: 30px !important;
        background: var(--input-bg) !important;
        box-shadow: none !important;
        border: none !important;
        outline: none !important;
    }}
    [data-testid="stChatInput"] textarea {{
        height: auto !important;
        min-height: 24px !important;
        padding: 12px !important;
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stChatInput"]:focus,
    [data-testid="stChatInput"]:focus-within,
    [data-testid="stChatInput"] textarea:focus,
    [data-testid="stChatInput"] input:focus,
    [data-testid="stChatInput"] textarea:focus-visible,
    [data-testid="stChatInput"] input:focus-visible {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        border-color: transparent !important;
    }}
    [data-testid="stChatInput"] *:focus,
    [data-testid="stChatInput"] *:focus-visible,
    [data-testid="stChatInput"] *:focus-within {{
        outline: none !important;
        box-shadow: none !important;
        border-color: transparent !important;
    }}
    [data-testid="stChatInput"] button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    .file-card {{
        background: white;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #eee;
        margin-top: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    footer {{display: none !important;}}
    header {{background: transparent !important;}}
    @media (max-width: 600px) {{
        .block-container {{
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .stChatInput {{ transform: translateY(-15vh); }}
    }}
</style>
"""

def apply_theme():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="auto"
    )
    # Inject Material Symbols
    st.markdown('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0" />', unsafe_allow_html=True)
    
    # Load current theme from config
    current_theme = get_theme()
    css_content = get_css(current_theme)
    
    st.markdown(css_content, unsafe_allow_html=True)

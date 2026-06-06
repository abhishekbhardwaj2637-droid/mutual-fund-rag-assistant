import sys
# SQLite workaround for Streamlit Cloud (Linux) where system sqlite3 is < 3.35.0 required by ChromaDB
if sys.platform.startswith('linux'):
    try:
        __import__('pysqlite3')
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    except ImportError:
        pass

import os
import streamlit as st

# Append current working directory to python path for imports
sys.path.append(os.getcwd())

import re
from core.orchestrator import handle_query

def markdown_to_html(text: str) -> str:
    # 1. Escape HTML
    text = (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;'))
            
    # 2. Parse bold **text** -> <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # 3. Parse markdown links [text](url) -> <a href="url" target="_blank" style="color: #4edea3; text-decoration: underline; font-weight: 500;">text</a>
    def replace_link(match):
        label = match.group(1)
        url = match.group(2).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return f'<a href="{url}" target="_blank" style="color: #4edea3; text-decoration: underline; font-weight: 500;">{label}</a>'
        
    text = re.sub(r'\[(.*?)\]\((.*?)\)', replace_link, text)
    
    # 4. Parse bullet lists
    lines = text.split('\n')
    in_list = False
    html_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('*') or stripped.startswith('-') or stripped.startswith('•'):
            if not in_list:
                html_lines.append('<ul style="padding-left: 20px; margin-top: 8px; margin-bottom: 8px; list-style-type: disc;">')
                in_list = True
            content = stripped[1:].strip()
            html_lines.append(f'<li style="margin-bottom: 6px; color: #dfe2f1; line-height: 1.6;">{content}</li>')
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(line)
            
    if in_list:
        html_lines.append('</ul>')
        
    result = '\n'.join(html_lines)
    result = result.replace('</ul>\n', '</ul>').replace('</li>\n', '</li>')
    result = result.replace('\n', '<br>')
    return result

# Set Streamlit Page Config
st.set_page_config(
    page_title="MintFlow AI | Mutual Fund Fact Finder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Obsidian Mint CSS Styling Injection (verbatim tokens from screen.png)
st.markdown("""
<style>
/* Load Google Fonts and Material Symbols */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* Apply Outfit and Inter fonts */
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}
h1, h2, h3, h4, h5, h6, .outfit-font {
    font-family: 'Outfit', sans-serif !important;
}

/* Base background styling */
.stApp {
    background-color: #0b0f19 !important;
    color: #dfe2f1 !important;
}

/* Hide Streamlit default header/footer and adjust top padding */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container {
    padding-top: 100px !important;
    padding-bottom: 80px !important;
}

/* 1. Global Top Disclaimer Banner (Solid Background) */
.compliance-banner {
    position: fixed;
    top: 0;
    z-index: 1000;
    background: #171b26 !important;
    border-bottom: 1px solid rgba(255, 185, 95, 0.15);
    padding: 6px 16px;
    text-align: center;
    color: #ffb95f;
    font-weight: 500;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}

/* 2. Top Header Navigation Bar (Solid Background) */
.top-header-bar {
    position: fixed;
    top: 32px;
    z-index: 999;
    background: #0b0f19 !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Webkit Scrollbar Styling */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0b0f19;
}
::-webkit-scrollbar-thumb {
    background: #171b26;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #4edea3;
}

/* Responsive Overlapping Fixes (Dynamic layout based on sidebar collapse state) */
/* Sidebar expanded (aria-expanded="true" or default) */
[data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stMain"] .top-header-bar,
[data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stMain"] .compliance-banner,
[data-testid="stSidebarNav"] ~ [data-testid="stMain"] .top-header-bar,
.top-header-bar, .compliance-banner {
    left: 336px !important;
    width: calc(100% - 336px) !important;
}
[data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stMain"] .footer-disclosures,
.footer-disclosures {
    left: 336px !important;
    width: calc(100% - 336px) !important;
}

/* Sidebar collapsed (aria-expanded="false") */
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"] .top-header-bar,
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"] .compliance-banner {
    left: 0 !important;
    width: 100% !important;
}
[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stMain"] .footer-disclosures {
    left: 0 !important;
    width: 100% !important;
}

/* Mobile screen constraints (screens <= 768px always use full-width headers) */
@media (max-width: 768px) {
    [data-testid="stSidebar"] ~ [data-testid="stMain"] .top-header-bar,
    [data-testid="stSidebar"] ~ [data-testid="stMain"] .compliance-banner {
        left: 0 !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] ~ [data-testid="stMain"] .footer-disclosures {
        left: 0 !important;
        width: 100% !important;
    }
}

.logo-section {
    display: flex;
    align-items: center;
    gap: 24px;
}
.logo-title {
    color: #4edea3;
    font-weight: 700;
    font-size: 22px;
    letter-spacing: -0.02em;
}
.nav-link-active {
    color: #4edea3 !important;
    font-weight: 600;
    border-bottom: 2px solid #4edea3;
    padding-bottom: 4px;
    text-decoration: none;
    font-size: 14px;
}
.nav-link {
    color: #bbcabf !important;
    text-decoration: none;
    font-size: 14px;
    transition: color 0.2s;
}
.nav-link:hover {
    color: #4edea3 !important;
}

.header-icons {
    display: flex;
    gap: 16px;
    align-items: center;
    color: #bbcabf;
}
.header-icon-btn {
    cursor: pointer;
    font-size: 22px !important;
    transition: color 0.2s;
}
.header-icon-btn:hover {
    color: #4edea3;
}

/* 3. Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background-color: #0f131d !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    padding-top: 120px !important;
}

.sidebar-title {
    color: #dfe2f1;
    font-weight: 700;
    font-size: 20px;
    margin-bottom: 4px;
}
.sidebar-subtitle {
    color: #bbcabf;
    font-size: 12px;
    opacity: 0.7;
    margin-bottom: 24px;
}

.supported-funds-header {
    font-size: 10px;
    text-transform: uppercase;
    font-weight: bold;
    margin-bottom: 8px;
    letter-spacing: 0.1em;
    color: #bbcabf;
    opacity: 0.5;
}

.fund-item {
    padding: 10px 12px;
    border-radius: 8px;
    color: #bbcabf !important;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
    transition: all 0.2s;
    border: 1px solid transparent;
    text-decoration: none !important;
}
.fund-item:hover {
    background: rgba(255, 255, 255, 0.03);
    color: #4edea3 !important;
}
.fund-item-active {
    background: rgba(16, 185, 129, 0.1) !important;
    color: #4edea3 !important;
    font-weight: 600;
    border: 1px solid rgba(78, 222, 163, 0.2) !important;
}

/* Compare Funds Sidebar Button */
.compare-funds-btn {
    display: block;
    width: 100%;
    background: #10b981;
    color: #003824 !important;
    text-align: center;
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    text-decoration: none;
    margin-top: 40px;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}
.compare-funds-btn:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
}

/* 4. Chat Container & Bubble Grid */
.chat-container {
    max-width: 900px;
    margin: 40px auto 140px auto;
}

.user-bubble-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 24px;
}
.user-bubble {
    background-color: #262a35;
    color: #dfe2f1;
    border-radius: 16px 16px 0px 16px;
    padding: 14px 20px;
    max-width: 75%;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.02);
    font-size: 15px;
    line-height: 1.5;
}

.assistant-bubble-wrapper {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    align-items: flex-start;
}
.assistant-icon-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(78, 222, 163, 0.15);
    border: 1px solid rgba(78, 222, 163, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.assistant-icon-bolt {
    color: #4edea3;
    font-size: 20px !important;
}

.assistant-bubble-factual {
    background: rgba(22, 29, 47, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px 16px 16px 0px;
    padding: 18px 22px;
    flex-grow: 1;
    max-width: 80%;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    font-size: 15px;
    line-height: 1.6;
}

/* Bullet list padding corrections (verbatim fix for Image 2) */
.assistant-bubble-factual ul, .assistant-bubble-refused ul {
    padding-left: 24px !important;
    margin-top: 10px !important;
    margin-bottom: 10px !important;
    list-style-position: outside !important;
}
.assistant-bubble-factual li, .assistant-bubble-refused li {
    margin-bottom: 6px !important;
}

.assistant-bubble-refused {
    background: rgba(22, 29, 47, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-left: 4px solid #ffb95f !important;
    border-radius: 16px 16px 16px 0px;
    padding: 18px 22px;
    flex-grow: 1;
    max-width: 80%;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    font-size: 15px;
    line-height: 1.6;
}

/* Verified Source Badge Styling (verbatim from screen.png) */
.citation-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 4px 10px;
    color: #dfe2f1 !important;
    font-size: 12px;
    font-weight: 500;
    text-decoration: none !important;
    transition: all 0.2s;
}
.citation-badge:hover {
    background: rgba(78, 222, 163, 0.1);
    border-color: rgba(78, 222, 163, 0.3);
    color: #4edea3 !important;
}

/* Redirect outline buttons for advisory query */
.redirect-btn {
    text-decoration: none !important;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    color: #dfe2f1 !important;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
}
.redirect-btn:hover {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.15);
}

/* 5. Custom Bottom Input Panel Alignment */
[data-testid="stChatInput"] {
    background: rgba(22, 29, 47, 0.7) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 16px !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5) !important;
    max-width: 900px !important;
    margin: 0 auto !important;
}
[data-testid="stChatInput"] textarea {
    color: #dfe2f1 !important;
    font-size: 15px !important;
}

/* Example Pill Buttons */
div.stButton > button {
    background-color: rgba(22, 29, 47, 0.7) !important;
    color: #bbcabf !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 20px !important;
    padding: 8px 18px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    width: auto !important;
    margin: 0 auto !important;
    display: block !important;
}
div.stButton > button:hover {
    border-color: rgba(78, 222, 163, 0.4) !important;
    color: #4edea3 !important;
    background-color: rgba(22, 29, 47, 0.9) !important;
}

/* 6. Footer Disclosures */
.footer-disclosures {
    position: fixed;
    bottom: 0;
    right: 0;
    width: calc(100% - 21rem);
    background: #0a0e18;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 98;
}
.footer-text {
    font-size: 11px;
    color: #ffb95f;
    opacity: 0.8;
}
.footer-links {
    display: flex;
    gap: 16px;
}
.footer-link-item {
    font-size: 11px;
    color: #bbcabf;
    text-decoration: underline;
}
.footer-link-item:hover {
    color: #4edea3;
}
</style>
""", unsafe_allow_html=True)

# 1. Render Global Disclaimer Banner
st.markdown('<div class="compliance-banner"><span class="material-symbols-outlined" style="font-size:16px;">gavel</span> Facts-Only RAG Assistant. Strictly no investment advice, speculations, or fund comparisons.</div>', unsafe_allow_html=True)

# 2. Render Top AppBar Header
st.markdown('<div class="top-header-bar"><div class="logo-section"><div class="logo-title outfit-font">MintFlow AI</div><div style="display: flex; gap: 20px;"><a href="#" class="nav-link-active outfit-font">Fact Finder</a><a href="#" class="nav-link outfit-font">Portfolio</a><a href="#" class="nav-link outfit-font">Analysis</a></div></div><div class="header-icons"><span class="material-symbols-outlined header-icon-btn">account_balance_wallet</span><span class="material-symbols-outlined header-icon-btn">account_circle</span></div></div>', unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pill_query" not in st.session_state:
    st.session_state.pill_query = None

# Check if a fund was selected from the sidebar links
selected_fund_slug = None
try:
    if "fund" in st.query_params:
        selected_fund_slug = st.query_params["fund"]
        # Clear query params to prevent loops on rerun
        st.query_params.clear()
except Exception:
    try:
        q_params = st.experimental_get_query_params()
        if "fund" in q_params:
            selected_fund_slug = q_params["fund"][0]
            st.experimental_set_query_params()
    except Exception:
        pass

if selected_fund_slug:
    slug_to_name = {
        "hdfc-silver-etf-fof-direct-growth": "HDFC Silver ETF FoF",
        "hdfc-small-cap-fund-direct-growth": "HDFC Small Cap Fund Direct Growth",
        "hdfc-defence-fund-direct-growth": "HDFC Defence Fund",
        "hdfc-gold-etf-fund-of-fund-direct-plan-growth": "HDFC Gold ETF Fund of Fund",
        "hdfc-mid-cap-fund-direct-growth": "HDFC Mid-Cap Opportunities Fund"
    }
    fund_name = slug_to_name.get(selected_fund_slug)
    if fund_name:
        st.session_state.pill_query = f"Show overview of {fund_name}"

# Scan history to get active slug
def get_active_slug():
    for msg in reversed(st.session_state.messages):
        if msg.get("detected_scheme"):
            return msg["detected_scheme"]
    return None

# Sidebar Rendering
def render_sidebar(active_slug=None):
    with st.sidebar:
        st.markdown('<div class="sidebar-title outfit-font">HDFC Mutual Funds</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-subtitle">AI Portfolio Assistant</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="supported-funds-header">Supported Funds</div>', unsafe_allow_html=True)
        
        funds = [
            ("Silver ETF FoF", "hdfc-silver-etf-fof-direct-growth", "trending_up"),
            ("Small Cap Fund", "hdfc-small-cap-fund-direct-growth", "account_balance"),
            ("Defence Fund", "hdfc-defence-fund-direct-growth", "pie_chart"),
            ("Gold ETF FoF", "hdfc-gold-etf-fund-of-fund-direct-plan-growth", "savings"),
            ("Mid-Cap Opp.", "hdfc-mid-cap-fund-direct-growth", "query_stats")
        ]
        
        for name, slug, icon in funds:
            is_active = (active_slug == slug)
            class_name = "fund-item fund-item-active" if is_active else "fund-item"
            # Clickable anchor tag
            st.markdown(f'<a href="?fund={slug}" target="_self" class="{class_name}"><span class="material-symbols-outlined" style="font-size:18px;">{icon}</span>{name}</a>', unsafe_allow_html=True)
            
        st.markdown('<a href="#" class="compare-funds-btn">Compare Funds</a>', unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="supported-funds-header">API Configurations</div>', unsafe_allow_html=True)
        gemini_key = st.text_input("Gemini API Key", value=os.environ.get("GEMINI_API_KEY", ""), type="password")
        if gemini_key and gemini_key != "your_gemini_api_key_here":
            os.environ["GEMINI_API_KEY"] = gemini_key
            
        openai_key = st.text_input("OpenAI API Key", value=os.environ.get("OPENAI_API_KEY", ""), type="password")
        if openai_key and openai_key != "your_openai_api_key_here":
            os.environ["OPENAI_API_KEY"] = openai_key
            
        if (gemini_key and gemini_key != "your_gemini_api_key_here") or (openai_key and openai_key != "your_openai_api_key_here"):
            st.markdown('<div style="color: #4edea3; font-size: 12px; margin-top: 8px;">🟢 Live Generative Mode</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: #ffb95f; font-size: 12px; margin-top: 8px;">🟡 Offline Fallback Mode</div>', unsafe_allow_html=True)


# Render Sidebar (detecting active scheme from history)
active_slug = get_active_slug()
render_sidebar(active_slug)

# Main Container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Example Query Pills Column Setup (centered)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("What is the expense ratio?"):
        st.session_state.pill_query = "What is the expense ratio of HDFC Small Cap Fund?"
with col2:
    if st.button("Who is the fund manager?"):
        st.session_state.pill_query = "Who is the fund manager of HDFC Defence Fund?"
with col3:
    if st.button("View exit load details"):
        st.session_state.pill_query = "What is the exit load for HDFC Mid-Cap Opportunities Fund?"

# Handle pill query if clicked
def process_user_query(query_text):
    # Add User Message to state
    st.session_state.messages.append({
        "role": "user",
        "content": query_text
    })
    
    # Run Orchestrator Pipeline
    with st.spinner("Retrieving facts..."):
        res = handle_query(query_text)
        
    # Check if a scheme was queried (to highlight sidebar)
    detected_scheme = None
    if "retrieved_chunks" in res and res["retrieved_chunks"]:
        detected_scheme = res["retrieved_chunks"][0]["scheme_slug"]
        
    # Append Assistant Message to state
    assistant_msg = {
        "role": "assistant",
        "content": res["response"],
        "status": res.get("status", "success"),
        "detected_scheme": detected_scheme
    }
    if res.get("status") == "refused":
        assistant_msg["links"] = res.get("links", [])
    else:
        assistant_msg["source_url"] = res.get("source_url")
        assistant_msg["last_updated"] = res.get("last_updated")
        
    st.session_state.messages.append(assistant_msg)
    st.rerun()

if st.session_state.pill_query:
    pq = st.session_state.pill_query
    st.session_state.pill_query = None
    process_user_query(pq)

st.markdown("<br><br>", unsafe_allow_html=True)

# Chat Feed Display
import time

for i, msg in enumerate(st.session_state.messages):
    is_last = (i == len(st.session_state.messages) - 1)
    
    if msg["role"] == "user":
        # Flat, non-indented string to prevent markdown code block formatting
        st.markdown(f'<div class="user-bubble-wrapper"><div class="user-bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
    else:
        # Format the assistant content to HTML to prevent markdown leaks
        if msg.get("status") == "refused":
            formatted_content = markdown_to_html(msg["content"])
            # Amber left border card for warnings / refusals
            links_html = ""
            if msg.get("links"):
                links_html = '<div style="display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap;">'
                for link in msg["links"]:
                    icon = link.get("icon", "verified_user")
                    links_html += f'<a href="{link["url"]}" target="_blank" class="redirect-btn"><span class="material-symbols-outlined" style="font-size:18px; color:#bbcabf;">{icon}</span><span>{link["name"]}</span></a>'
                links_html += '</div>'
                
            # Flat HTML output to prevent code block leaks
            st.markdown(f'<div class="assistant-bubble-wrapper"><div class="assistant-icon-circle"><span class="material-symbols-outlined assistant-icon-bolt">bolt</span></div><div class="assistant-bubble-refused"><div>{formatted_content}</div>{links_html}</div></div>', unsafe_allow_html=True)
        else:
            # Factual RAG answer
            source_html = ""
            if msg.get("source_url") and msg["source_url"] != "https://groww.in":
                logo_url = "https://lh3.googleusercontent.com/aida-public/AB6AXuDCmKfQ8hUGfpXp71osm6b8Pnxem_ozsNYdECtLQTuXicOvmP0WtUXgj-d8gJl8bh8nVy_u-bTOJIqa0yRyBNNepAiVut31hEVvL9-zChW850oxaPPpNI4nWZ2Ew6VMGnqIFY_I7aEpXpdZfRNJUuO0lAfLF5RgNjjeTMljW8Ymvx8JgP2ki0c0mMwUo7R7bZxbTw60xUb00N9fkvMsIIRt_Naq34mrdItsKVpoP3K2gI-eklTW4qpHBtI8YWpqXdurDEUMSY3uUxM"
                source_html = f'<div style="display: flex; align-items: center; gap: 6px; margin-top: 14px; font-size: 13px; color: #bbcabf;"><span>Verified Source:</span><a href="{msg["source_url"]}" target="_blank" class="citation-badge"><img src="{logo_url}" style="width: 14px; height: 14px; border-radius: 50%;" /><span>Groww Official SID Citation</span><span class="material-symbols-outlined" style="font-size: 14px; margin-left: 2px;">open_in_new</span></a></div>'
            
            footer_html = f'<div style="text-align: right; font-size: 10px; color: #bbcabf; opacity: 0.5; margin-top: 8px;">Last updated from sources: {msg.get("last_updated", "N/A")}</div>'
            
            if is_last and not msg.get("streamed"):
                placeholder = st.empty()
                words = msg["content"].split()
                current_text = ""
                for word in words:
                    current_text += word + " "
                    formatted_content = markdown_to_html(current_text)
                    placeholder.markdown(f'<div class="assistant-bubble-wrapper"><div class="assistant-icon-circle"><span class="material-symbols-outlined assistant-icon-bolt">bolt</span></div><div class="assistant-bubble-factual"><div>{formatted_content}</div>{source_html}{footer_html}</div></div>', unsafe_allow_html=True)
                    time.sleep(0.04)
                msg["streamed"] = True
            else:
                formatted_content = markdown_to_html(msg["content"])
                st.markdown(f'<div class="assistant-bubble-wrapper"><div class="assistant-icon-circle"><span class="material-symbols-outlined assistant-icon-bolt">bolt</span></div><div class="assistant-bubble-factual"><div>{formatted_content}</div>{source_html}{footer_html}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# User Chat Input
user_input = st.chat_input("Ask about expense ratios, fund managers, or portfolio holdings...")
if user_input:
    process_user_query(user_input)

# Custom Input Sub-caption
st.markdown('<div class="input-disclaimer">AI-generated responses can be inaccurate. Always verify against the original Fund Document.</div>', unsafe_allow_html=True)

# 6. Global Page Footer
st.markdown('<div class="footer-disclosures"><div class="footer-text">© 2024 MintFlow AI. SEBI Registered Investment Advisor. Mutual fund investments are subject to market risks.</div><div class="footer-links"><a href="#" class="footer-link-item">Risk Disclosures</a><a href="#" class="footer-link-item">Privacy Policy</a><a href="#" class="footer-link-item">Terms of Service</a></div></div>', unsafe_allow_html=True)

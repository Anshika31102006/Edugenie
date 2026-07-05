# main_app.py — EduGenie 🌈 (Enhanced UI Edition)

import streamlit as st
from dotenv import load_dotenv
import os

# Import tool modules
from pdf_summarizer import run_pdf_summarizer
from chatbot import run_chatbot
from podcast_generator import run_podcast_generator
from flashcard_generator import run_flashcard_generator

# Load API Key
load_dotenv()

# Initialize Theme State
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# ------------------------------
# 🌟 Streamlit Page Configuration
# ------------------------------
st.set_page_config(
    page_title="EduGenie - Your AI Learning Companion",
    page_icon="🎓",
    layout="wide"
)

# ------------------------------
# 🔑 Sidebar AI & API Configuration
# ------------------------------
st.sidebar.title("🔑 AI Settings")
provider = st.sidebar.selectbox(
    "Select AI Provider",
    ["Offline / Local Mode (Free)", "OpenAI", "Groq"],
    help="Choose 'Offline/Local Mode' to run the app for free without keys, or choose OpenAI/Groq for premium AI."
)

api_key = ""
if provider == "OpenAI":
    env_key = os.getenv("OPENAI_API_KEY", "")
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=env_key,
        type="password",
        help="Provide your OpenAI API key."
    )
elif provider == "Groq":
    env_key = os.getenv("GROQ_API_KEY", "")
    api_key = st.sidebar.text_input(
        "Groq API Key",
        value=env_key,
        type="password",
        help="Provide your Groq API key."
    )

st.session_state.llm_provider = provider
st.session_state.openai_api_key = api_key  # for backward compatibility
st.session_state.api_key = api_key

# ------------------------------
# 💫 Custom CSS Styling (Dynamic Themes)
# ------------------------------
if st.session_state.theme_mode == "dark":
    theme_css = """
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

        /* Global Font and Background */
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at 50% 0%, #17182c 0%, #0a0a14 100%) !important;
            background-attachment: fixed !important;
            color: #d1d2f9 !important;
            font-family: 'Outfit', sans-serif !important;
        }

        [data-testid="stHeader"] {
            background: rgba(10, 10, 20, 0.5) !important;
            backdrop-filter: blur(12px) !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: #06060c !important;
            border-right: 1px solid rgba(169, 112, 255, 0.1) !important;
        }

        /* Force text colors in Dark Mode */
        body, p, span, label, li, h1, h2, h3, h4, h5, h6, input, textarea, select, .stWidgetLabel, .stWidgetLabel p, div[data-testid="stMarkdownContainer"] p {
            color: #d1d2f9 !important;
            font-family: 'Outfit', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }

        /* Specific overrides for buttons to keep text white and legible */
        .stButton > button span, .stButton > button p {
            color: #ffffff !important;
        }
        
        .stButton > button:hover span, .stButton > button:hover p {
            color: #ffffff !important;
        }

        /* Specific overrides for chats */
        [data-testid="stChatMessageContent"] p,
        [data-testid="stChatMessageContent"] span {
            color: #e6e6fa !important;
        }

        /* Fix select slider and radio labels in Dark Mode */
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label span,
        div[data-testid="stSlider"] p,
        div[data-testid="stSlider"] span {
            color: #d1d2f9 !important;
        }

        /* Centering and Title Styling */
        .main-title {
            font-size: 3.8rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #bd93f9 0%, #00f0ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.1em;
            filter: drop-shadow(0 2px 15px rgba(169, 112, 255, 0.25));
        }

        .subtitle {
            font-size: 1.25rem;
            text-align: center;
            color: #a0a0c5;
            margin-bottom: 2em;
            font-family: 'Outfit', sans-serif;
        }

        /* Tool Selection Cards (Buttons) */
        .stButton > button {
            background: rgba(20, 20, 35, 0.65) !important;
            border: 1px solid rgba(169, 112, 255, 0.18) !important;
            border-radius: 16px !important;
            font-size: 1.1rem !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            padding: 16px 0 !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(8px) !important;
            transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            font-family: 'Outfit', sans-serif !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #7c3aed, #06b6d4) !important;
            color: #ffffff !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 30px rgba(124, 58, 237, 0.45) !important;
            border-color: transparent !important;
        }

        /* Theme Toggle Button specific fixed positioning inside header */
        button[data-testid="stBaseButton-theme_toggle_btn"] {
            position: fixed !important;
            top: 12px !important;
            right: 15px !important;
            z-index: 999999 !important;
            border-radius: 50% !important;
            width: 42px !important;
            height: 42px !important;
            padding: 0 !important;
            font-size: 1.25rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: rgba(30, 30, 50, 0.7) !important;
            border: 1px solid rgba(169, 112, 255, 0.25) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.3s ease !important;
        }

        button[data-testid="stBaseButton-theme_toggle_btn"]:hover {
            background: #bd93f9 !important;
            box-shadow: 0 0 15px rgba(189, 147, 249, 0.6) !important;
            color: white !important;
        }

        /* Streamlit File Uploader styling */
        div[data-testid="stFileUploader"] {
            background-color: rgba(15, 15, 25, 0.5) !important;
            border: 2px dashed rgba(169, 112, 255, 0.25) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            margin-bottom: 25px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stFileUploader"]:hover {
            border-color: #00f0ff !important;
            background-color: rgba(20, 20, 35, 0.7) !important;
        }

        div[data-testid="stFileDropzone"] {
            background-color: transparent !important;
            color: #a0a0c5 !important;
        }

        /* Alert Boxes Styling */
        div[data-testid="stAlert"] {
            border-radius: 16px !important;
            background-color: rgba(25, 25, 45, 0.6) !important;
            border: 1px solid rgba(169, 112, 255, 0.18) !important;
            color: #d1d2f9 !important;
        }

        div[data-testid="stAlert"] p {
            color: #d1d2f9 !important;
        }

        /* Input Controls and Textboxes */
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
            background-color: rgba(15, 15, 25, 0.8) !important;
            color: #ffffff !important;
            border: 1px solid rgba(169, 112, 255, 0.18) !important;
            border-radius: 12px !important;
        }

        div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
            border-color: #00f0ff !important;
            box-shadow: 0 0 10px rgba(0, 240, 255, 0.25) !important;
        }

        /* Footer styling */
        .footer {
            text-align: center;
            color: #72728d;
            font-size: 0.9rem;
            padding-top: 1.5em;
            border-top: 1px solid rgba(169, 112, 255, 0.1);
            margin-top: 3.5em;
            font-family: 'Outfit', sans-serif;
        }
    """
else:
    theme_css = """
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

        /* Global Font and Background (Warm Sky Blue Theme) */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #e0f2fe 100%) !important;
            background-attachment: fixed !important;
            color: #0c4a6e !important;
            font-family: 'Outfit', sans-serif !important;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.4) !important;
            backdrop-filter: blur(12px) !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: #f0f9ff !important;
            border-right: 1px solid rgba(3, 105, 161, 0.1) !important;
        }

        /* Force text colors in Light Mode */
        body, p, span, label, li, h1, h2, h3, h4, h5, h6, input, textarea, select, .stWidgetLabel, .stWidgetLabel p, div[data-testid="stMarkdownContainer"] p {
            color: #0c4a6e !important;
            font-family: 'Outfit', sans-serif !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #0369a1 !important;
        }

        /* Specific overrides for buttons in Light Mode */
        .stButton > button span, .stButton > button p {
            color: #0284c7 !important;
        }
        
        .stButton > button:hover span, .stButton > button:hover p {
            color: #ffffff !important;
        }

        /* Specific overrides for chats in Light Mode */
        [data-testid="stChatMessageContent"] p,
        [data-testid="stChatMessageContent"] span {
            color: #0c4a6e !important;
        }

        /* Fix select slider and radio labels in Light Mode */
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label span,
        div[data-testid="stSlider"] p,
        div[data-testid="stSlider"] span {
            color: #0c4a6e !important;
        }

        /* Centering and Title Styling */
        .main-title {
            font-size: 3.8rem;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #0369a1 0%, #0891b2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.1em;
            filter: drop-shadow(0 2px 10px rgba(3, 105, 161, 0.15));
        }

        .subtitle {
            font-size: 1.25rem;
            text-align: center;
            color: #0369a1;
            margin-bottom: 2em;
            font-family: 'Outfit', sans-serif;
        }

        /* Tool Selection Cards (Buttons) */
        .stButton > button {
            background: rgba(255, 255, 255, 0.75) !important;
            border: 1px solid rgba(3, 105, 161, 0.2) !important;
            border-radius: 16px !important;
            font-size: 1.1rem !important;
            color: #0369a1 !important;
            font-weight: 600 !important;
            padding: 16px 0 !important;
            box-shadow: 0 6px 20px 0 rgba(3, 105, 161, 0.06) !important;
            backdrop-filter: blur(8px) !important;
            transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            font-family: 'Outfit', sans-serif !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #0284c7, #0891b2) !important;
            color: #ffffff !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 10px 25px rgba(2, 132, 199, 0.3) !important;
            border-color: transparent !important;
        }

        /* Theme Toggle Button specific fixed positioning inside header */
        button[data-testid="stBaseButton-theme_toggle_btn"] {
            position: fixed !important;
            top: 12px !important;
            right: 15px !important;
            z-index: 999999 !important;
            border-radius: 50% !important;
            width: 42px !important;
            height: 42px !important;
            padding: 0 !important;
            font-size: 1.25rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: rgba(255, 255, 255, 0.8) !important;
            border: 1px solid rgba(3, 105, 161, 0.25) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            transition: all 0.3s ease !important;
        }

        button[data-testid="stBaseButton-theme_toggle_btn"]:hover {
            background: #0284c7 !important;
            box-shadow: 0 0 15px rgba(2, 132, 199, 0.5) !important;
            color: white !important;
        }

        /* Streamlit File Uploader styling */
        div[data-testid="stFileUploader"] {
            background-color: rgba(255, 255, 255, 0.5) !important;
            border: 2px dashed rgba(3, 105, 161, 0.2) !important;
            border-radius: 16px !important;
            padding: 24px !important;
            margin-bottom: 25px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stFileUploader"]:hover {
            border-color: #0891b2 !important;
            background-color: rgba(255, 255, 255, 0.8) !important;
        }

        div[data-testid="stFileDropzone"] {
            background-color: transparent !important;
            color: #0369a1 !important;
        }

        /* Alert Boxes Styling */
        div[data-testid="stAlert"] {
            border-radius: 16px !important;
            background-color: rgba(255, 255, 255, 0.7) !important;
            border: 1px solid rgba(3, 105, 161, 0.15) !important;
            color: #0c4a6e !important;
        }

        div[data-testid="stAlert"] p {
            color: #0c4a6e !important;
        }

        /* Input Controls and Textboxes */
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
            background-color: rgba(255, 255, 255, 0.85) !important;
            color: #0c4a6e !important;
            border: 1px solid rgba(3, 105, 161, 0.18) !important;
            border-radius: 12px !important;
        }

        div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
            border-color: #0891b2 !important;
            box-shadow: 0 0 10px rgba(8, 145, 178, 0.15) !important;
        }

        .footer {
            text-align: center;
            color: #0369a1;
            font-size: 0.9rem;
            padding-top: 1.5em;
            border-top: 1px solid rgba(3, 105, 161, 0.1);
            margin-top: 3.5em;
            font-family: 'Outfit', sans-serif;
        }
    """

st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)

# ------------------------------
# 🧠 Main Title Section with Centered Header
# ------------------------------
st.markdown("<h1 class='main-title'>EduGenie 🎓</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your AI-powered Learning Assistant for Smarter Study Sessions</p>", unsafe_allow_html=True)
st.markdown("")

# ------------------------------
# 🌓 Theme Toggle Button (Fixed Position at Top Right Header)
# ------------------------------
theme_icon = "🌙" if st.session_state.theme_mode == "light" else "☀️"
theme_help = "Switch to Dark Mode" if st.session_state.theme_mode == "light" else "Switch to Light Mode"
if st.button(theme_icon, help=theme_help, key="theme_toggle_btn"):
    st.session_state.theme_mode = "dark" if st.session_state.theme_mode == "light" else "light"
    st.rerun()

# ------------------------------
# 🧩 Feature Buttons as Cards
# ------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄 Summarize PDF", use_container_width=True):
        st.session_state.tool_selector = "summarizer"

with col2:
    if st.button("💬 Chat with PDF", use_container_width=True):
        st.session_state.tool_selector = "chatbot"

with col3:
    if st.button("🎧 Generate Podcast", use_container_width=True):
        st.session_state.tool_selector = "podcast"

with col4:
    if st.button("🧠 Practice (Flashcards)", use_container_width=True):
        st.session_state.tool_selector = "flashcards"

# Initialize session state
if "tool_selector" not in st.session_state:
    st.session_state.tool_selector = None

st.markdown("---")

# ------------------------------
# 🚀 Launch Selected Tool
# ------------------------------
if st.session_state.tool_selector == "summarizer":
    run_pdf_summarizer()

elif st.session_state.tool_selector == "chatbot":
    run_chatbot()

elif st.session_state.tool_selector == "podcast":
    run_podcast_generator()

elif st.session_state.tool_selector == "flashcards":
    run_flashcard_generator()

else:
    st.info("👆 Select a feature above to begin using EduGenie!")

# ------------------------------
# 🌈 Footer Section
# ------------------------------
st.markdown(
    "<div class='footer'>✨ EduGenie © 2025 | Built with ❤️ using Streamlit & OpenAI</div>",
    unsafe_allow_html=True
)

# # main_app.py — EduGenie 🌈

# import streamlit as st
# from dotenv import load_dotenv
# import os
# from openai import OpenAI

# # Import individual tool modules
# from pdf_summarizer import run_pdf_summarizer
# from chatbot import run_chatbot
# from podcast_generator import run_podcast_generator
# from flashcard_generator import run_flashcard_generator

# # Load API Key
# load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")

# if not openai_api_key:
#     st.error("🚨 OPENAI_API_KEY not found! Please add it to your .env file.")
# else:
#     client = OpenAI(api_key=openai_api_key)

# # ------------------------------
# # 🌟 Streamlit Page Configuration
# # ------------------------------
# st.set_page_config(
#     page_title="EduGenie - Your AI Learning Companion",
#     page_icon="🎓",
#     layout="wide"
# )

# # ------------------------------
# # 💫 App Header & Styling
# # ------------------------------
# st.markdown("""
#     <style>
#         body {
#             background-color: #0E1117;
#             color: #FFFFFF;
#         }
#         .main-title {
#             font-size: 3rem;
#             font-weight: 800;
#             color: #a970ff;
#             text-align: center;
#             margin-bottom: 0;
#         }
#         .subtitle {
#             font-size: 1.2rem;
#             text-align: center;
#             color: #bbb;
#         }
#         .tool-card {
#             border-radius: 20px;
#             padding: 25px;
#             background-color: #1e1e2f;
#             box-shadow: 0px 0px 12px rgba(169, 112, 255, 0.3);
#             transition: all 0.3s ease-in-out;
#             cursor: pointer;
#         }
#         .tool-card:hover {
#             background-color: #292946;
#             transform: scale(1.02);
#         }
#     </style>
# """, unsafe_allow_html=True)

# # ------------------------------
# # 🧩 Main Title
# # ------------------------------
# st.markdown("<h1 class='main-title'>EduGenie 🎓</h1>", unsafe_allow_html=True)
# st.markdown("<p class='subtitle'>Your AI-powered Learning Assistant for smarter study sessions</p>", unsafe_allow_html=True)
# st.markdown("---")

# # ------------------------------
# # 🧠 Tool Selector Cards
# # ------------------------------
# col1, col2, col3, col4 = st.columns(4)

# with col1:
#     if st.button("📄 Summarize PDF", use_container_width=True):
#         st.session_state.tool_selector = "summarizer"

# with col2:
#     if st.button("💬 Chat with PDF", use_container_width=True):
#         st.session_state.tool_selector = "chatbot"

# with col3:
#     if st.button("🎧 Generate Podcast", use_container_width=True):
#         st.session_state.tool_selector = "podcast"

# with col4:
#     if st.button("🧠 Practice (Flashcards)", use_container_width=True):
#         st.session_state.tool_selector = "flashcards"

# # Initialize default session state
# if "tool_selector" not in st.session_state:
#     st.session_state.tool_selector = None

# # ------------------------------
# # 🚀 Conditional Feature Launcher
# # ------------------------------
# if st.session_state.tool_selector == "summarizer":
#     run_pdf_summarizer()

# elif st.session_state.tool_selector == "chatbot":
#     run_chatbot()

# elif st.session_state.tool_selector == "podcast":
#     run_podcast_generator()

# elif st.session_state.tool_selector == "flashcards":
#     run_flashcard_generator()

# else:
#     st.info("👆 Select a feature above to begin using EduGenie!")

# # ------------------------------
# # 🌈 Footer
# # ------------------------------
# st.markdown("---")
# st.markdown(
#     "<p style='text-align:center; color:gray;'>✨ EduGenie © 2025 | Built with ❤️ using Streamlit & OpenAI</p>",
#     unsafe_allow_html=True
# )
# main_app.py — EduGenie 🌈 (Enhanced UI Edition)

import streamlit as st
from dotenv import load_dotenv
import os
from openai import OpenAI

# Import tool modules
from pdf_summarizer import run_pdf_summarizer
from chatbot import run_chatbot
from podcast_generator import run_podcast_generator
from flashcard_generator import run_flashcard_generator

# Load API Key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("🚨 OPENAI_API_KEY not found! Please add it to your .env file.")
else:
    client = OpenAI(api_key=openai_api_key)

# ------------------------------
# 🌟 Streamlit Page Configuration
# ------------------------------
st.set_page_config(
    page_title="EduGenie - Your AI Learning Companion",
    page_icon="🎓",
    layout="wide"
)

# ------------------------------
# 💫 Custom CSS Styling
# ------------------------------
st.markdown("""
    <style>
        /* Background Gradient */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #b3e5fc, #e3f2fd, #bbdefb);
            background-attachment: fixed;
            color: #0d1117;
            font-family: "Poppins", sans-serif;
        }

        /* Centering and Title Styling */
        .main-title {
            font-size: 3.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #007BFF, #00C6FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.3em;
        }
        .subtitle {
            font-size: 1.2rem;
            text-align: center;
            color: #0d47a1;
            margin-bottom: 1.5em;
        }

        /* Tool Cards */
        .stButton > button {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            border-radius: 16px;
            font-size: 1.1rem;
            color: #0d47a1;
            font-weight: 600;
            padding: 15px 0;
            box-shadow: 0 4px 20px rgba(0, 105, 255, 0.15);
            transition: all 0.3s ease-in-out;
        }

        .stButton > button:hover {
            background: linear-gradient(90deg, #42a5f5, #5c6bc0);
            color: white;
            transform: scale(1.05);
            box-shadow: 0 4px 30px rgba(0, 105, 255, 0.25);
        }

        /* Footer */
        .footer {
            text-align: center;
            color: #0d47a1;
            font-size: 0.9rem;
            padding-top: 1.5em;
            border-top: 1px solid rgba(13, 71, 161, 0.2);
            margin-top: 2em;
        }

        /* Info box */
        .stAlert {
            border-radius: 16px;
            background-color: rgba(255, 255, 255, 0.6);
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# 🧠 Main Title Section
# ------------------------------
st.markdown("<h1 class='main-title'>EduGenie 🎓</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your AI-powered Learning Assistant for Smarter Study Sessions</p>", unsafe_allow_html=True)
st.markdown("")

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

# chatbot.py

import os
from io import BytesIO
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI
import streamlit as st

# 🔐 Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found in .env file.")
    st.stop()

# 🤖 Initialize OpenAI client
client = OpenAI(api_key=api_key)

# 📄 Extract all text from PDF
def extract_pdf_text(file_stream):
    text = ""
    try:
        reader = PdfReader(file_stream)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        st.error(f"❌ PDF read error: {e}")
    return text


# 🚀 Run Chatbot UI
def run_chatbot():
    st.markdown("""
    <h1 style='color: #5e1f8c; font-family: "Segoe UI", sans-serif;'>Ask Your PDF</h1>
    <p style='color: #5e1f8c; font-size: 1.1rem; font-family: "Segoe UI", sans-serif;'>Chat with your PDF and get instant answers from its content.</p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload your PDF here!", type="pdf")

    if uploaded_file:
        st.success(f"📄 {uploaded_file.name} uploaded successfully!")
        pdf_text = extract_pdf_text(BytesIO(uploaded_file.read()))

        if not pdf_text.strip():
            st.error("⚠ No readable text found in the PDF.")
            return

        # Persistent chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.markdown("🧠 *Ask me anything about your PDF!*")

        # Display existing chat history
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

        # Input box for user query
        user_input = st.chat_input("Ask a question about the PDF content")

        if user_input:
            st.chat_message("user").markdown(user_input)
            st.session_state.chat_history.append(("user", user_input))

            with st.spinner("Thinking..."):
                try:
                    # OpenAI Chat Completion
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",  # lightweight & fast
                        messages=[
                            {
                                "role": "system",
                                "content": f"You are a helpful assistant that answers only based on the provided PDF content:\n\n{pdf_text[:8000]}"
                            },
                            {
                                "role": "user",
                                "content": user_input
                            }
                        ],
                        temperature=0.3
                    )

                    reply = response.choices[0].message.content.strip()

                    st.chat_message("assistant").markdown(reply)
                    st.session_state.chat_history.append(("assistant", reply))

                except Exception as e:
                    st.error(f"❌ Error generating response: {e}")

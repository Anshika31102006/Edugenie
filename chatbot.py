import os
import re
from io import BytesIO
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from openai import OpenAI
from groq import Groq
import streamlit as st

load_dotenv()

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


# 🧠 Local offline chatbot query solver
def local_chat_response(query, pdf_text):
    paragraphs = [p.strip() for p in pdf_text.split('\n\n') if len(p.strip()) > 40]
    if not paragraphs:
        paragraphs = [p.strip() for p in pdf_text.split('\n') if len(p.strip()) > 40]
        
    query_words = set(re.findall(r'\w+', query.lower()))
    stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'for', 'on', 'with', 'as', 'at', 'by', 'an', 'be', 'this', 'that', 'from', 'it', 'its', 'they', 'them', 'how', 'what', 'why', 'where', 'who', 'when', 'you', 'your', 'me', 'i', 'can', 'could', 'should', 'would'])
    query_words = query_words - stopwords
    
    if not query_words:
        return "Please ask a question about specific terms or concepts in the PDF document."
        
    best_paragraph = ""
    max_matches = 0
    
    for p in paragraphs:
        p_words = set(re.findall(r'\w+', p.lower()))
        matches = len(query_words.intersection(p_words))
        if matches > max_matches:
            max_matches = matches
            best_paragraph = p
            
    if max_matches > 0:
        return f"*(Offline Search Mode)* I found this matching section in the document:\n\n{best_paragraph}"
    else:
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', pdf_text)
        fallback = " ".join([s.strip() for s in sentences[:4] if len(s.strip()) > 10])
        return f"*(Offline Search Mode)* I couldn't find a direct match for that. Here is some general context from the document:\n\n{fallback}"


# 🚀 Run Chatbot UI
def run_chatbot():
    st.markdown("""
    <h1 style='color: #5e1f8c; font-family: "Segoe UI", sans-serif;'>Ask Your PDF</h1>
    <p style='color: #5e1f8c; font-size: 1.1rem; font-family: "Segoe UI", sans-serif;'>Chat with your PDF and get instant answers from its content.</p>
    """, unsafe_allow_html=True)

    provider = st.session_state.get("llm_provider", "Offline / Local Mode (Free)")
    api_key = st.session_state.get("api_key") or os.getenv(f"{provider.upper()}_API_KEY")

    if provider != "Offline / Local Mode (Free)" and not api_key:
        st.warning(f"🔑 {provider} API Key is missing. Please provide it in the sidebar or select 'Offline / Local Mode (Free)' to run for free.")
        return

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
                    if provider == "Offline / Local Mode (Free)":
                        reply = local_chat_response(user_input, pdf_text)
                    else:
                        client = OpenAI(api_key=api_key) if provider == "OpenAI" else Groq(api_key=api_key)
                        model = "gpt-4o-mini" if provider == "OpenAI" else "llama-3.3-70b-versatile"
                        response = client.chat.completions.create(
                            model=model,
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
                    st.error(f"❌ Error generating response via {provider}: {e}")

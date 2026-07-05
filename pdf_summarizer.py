# # pdf_summarizer.py

# import fitz  # PyMuPDF
# from transformers import pipeline
# import streamlit as st
# import textwrap
# import re
# import time

# # 💜 Streamlit UI Styling
# st.markdown("""
# <style>
# div[data-testid="stFileUploader"] label { display: none !important; }
# div[data-testid="stFileUploader"] {
#     background-color: #f1e6ff !important;
#     border: 2px solid #5e1f8c !important;
#     border-radius: 12px !important;
#     padding: 20px !important;
#     margin-bottom: 25px !important;
# }
# div[data-testid="stFileDropzone"] {
#     background-color: #f1e6ff !important;
#     color: #5e1f8c !important;
#     border: 1px dashed #b57cff !important;
#     border-radius: 10px !important;
# }
# [data-testid="stNotificationContentInfo"],
# [data-testid="stNotificationContentSuccess"],
# [data-testid="stNotificationContentError"] {
#     color: #5e1f8c !important;
#     font-family: 'Segoe UI', sans-serif !important;
# }
# h1, h2, h3, h4, h5, h6, .stMarkdown p {
#     color: #5e1f8c !important;
#     font-family: 'Segoe UI', sans-serif !important;
# }
# </style>
# """, unsafe_allow_html=True)

# # 🧹 Clean text utility
# def clean_text(text):
#     text = text.replace('\u00a0', ' ')
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# # 📘 Extract text from PDF
# def extract_text_from_pdf(pdf_file):
#     text = ""
#     with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
#         for page in doc:
#             text += page.get_text()
#     return text

# # ⚙️ Load a faster summarization model
# @st.cache_resource
# def load_summarizer():
#     # Use a smaller, faster model than bart-large-cnn
#     return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# summarizer = load_summarizer()

# # ✂️ Split text & summarize in chunks
# def summarize_text_to_bullets(text, max_chunk_size=800):
#     chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
#     bullet_points = []
    
#     progress = st.progress(0)
#     total = len(chunks)
    
#     for i, chunk in enumerate(chunks):
#         progress.progress((i + 1) / total)
#         try:
#             result = summarizer(chunk, max_length=120, min_length=40, do_sample=False)[0]['summary_text']
#             sentences = result.split('. ')
#             for sentence in sentences:
#                 cleaned = clean_text(sentence.strip())
#                 if cleaned:
#                     bullet_points.append(f"• {textwrap.fill(cleaned, width=100)}")
#         except Exception as e:
#             bullet_points.append(f"⚠️ Error summarizing chunk {i+1}: {e}")
#         time.sleep(0.2)
    
#     progress.empty()
#     return "\n\n".join(bullet_points)

# # 🚀 Run PDF Summarizer App
# def run_pdf_summarizer():
#     st.markdown("""
#     <h1 style='color: #a970ff; font-family: "Segoe UI", sans-serif;'>AI-Powered PDF Summarizer</h1>
#     <p style='color: #a970ff; font-size: 1.1rem; font-family: "Segoe UI", sans-serif;'>Upload a PDF and get crisp, bulleted notes in seconds!</p>
#     """, unsafe_allow_html=True)

#     uploaded_file = st.file_uploader("📄 Upload your PDF", type=["pdf"])

#     if uploaded_file:
#         st.info("⏳ Extracting and summarizing your document...")
#         try:
#             raw_text = extract_text_from_pdf(uploaded_file)

#             if not raw_text.strip():
#                 st.error("❌ No readable text found in the PDF.")
#                 return

#             cleaned_text = clean_text(raw_text)
#             summary = summarize_text_to_bullets(cleaned_text)

#             st.success("✅ Summary Generated!")
#             st.markdown("<h3 style='color: #5e1f8c;'>📌 Summary:</h3>", unsafe_allow_html=True)
#             st.markdown(f"<div style='color: #5e1f8c; white-space: pre-wrap; font-family: Segoe UI;'>{summary}</div>", unsafe_allow_html=True)

#             st.download_button(
#                 label="📥 Download Summary (.txt)",
#                 data=summary,
#                 file_name="summary_output.txt",
#                 mime="text/plain"
#             )
#         except Exception as e:
#             st.error(f"❌ An error occurred: {e}")
# pdf_summarizer.py

import os
import fitz  # PyMuPDF
import re
import textwrap
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq

load_dotenv()

# 💜 Apply purple UI theme
st.markdown("""
<style>
div[data-testid="stFileUploader"] label { display: none !important; }
div[data-testid="stFileUploader"] {
    background-color: #f1e6ff !important;
    border: 2px solid #5e1f8c !important;
    border-radius: 12px !important;
    padding: 20px !important;
    margin-bottom: 25px !important;
}
div[data-testid="stFileDropzone"] {
    background-color: #f1e6ff !important;
    color: #5e1f8c !important;
    border: 1px dashed #b57cff !important;
    border-radius: 10px !important;
}
[data-testid="stNotificationContentInfo"],
[data-testid="stNotificationContentSuccess"],
[data-testid="stNotificationContentError"] {
    color: #5e1f8c !important;
    font-family: 'Segoe UI', sans-serif !important;
}
h1, h2, h3, h4, h5, h6, .stMarkdown p {
    color: #5e1f8c !important;
    font-family: 'Segoe UI', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# 🧹 Clean text
def clean_text(text):
    text = text.replace('\u00a0', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# 📄 Extract PDF text
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ✂️ Split large text into smaller chunks
def chunk_text(text, chunk_size=3000):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# 🧠 Summarize one chunk using selected API provider
def summarize_chunk(chunk, client, provider):
    prompt = f"""
    Summarize the following text into clear, concise bullet points focusing on key ideas, definitions, and facts.

    Text:
    {chunk}

    Return output as bullet points only, like:
    • Point 1
    • Point 2
    • Point 3
    """
    model = "gpt-4o-mini" if provider == "OpenAI" else "llama-3.3-70b-versatile"
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error summarizing chunk via {provider}: {e}"

# 🧠 Local extractive summarization fallback (No API Key required)
def local_summarize(text, num_bullets=10):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    if not sentences:
        return "• No clear sentences could be extracted from this PDF for the summary."
    
    # Simple word frequency scoring (Luhn's Algorithm)
    words = re.findall(r'\w+', text.lower())
    stopwords = set(['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'for', 'on', 'with', 'as', 'at', 'by', 'an', 'be', 'this', 'that', 'from', 'it', 'its', 'they', 'them', 'you', 'your', 'i', 'we', 'us', 'our'])
    word_freq = {}
    for w in words:
        if w not in stopwords:
            word_freq[w] = word_freq.get(w, 0) + 1
            
    sentence_scores = []
    for s in sentences:
        score = 0
        s_words = re.findall(r'\w+', s.lower())
        for w in s_words:
            if w in word_freq:
                score += word_freq[w]
        sentence_scores.append((score / max(1, len(s_words)), s))
        
    sentence_scores.sort(key=lambda x: x[0], reverse=True)
    top_sentences = sentence_scores[:num_bullets]
    
    summary_bullets = []
    for s in sentences:
        if s in [x[1] for x in top_sentences]:
            summary_bullets.append(f"• {s}")
            if len(summary_bullets) >= num_bullets:
                break
    return "\n\n".join(summary_bullets)

# 🚀 Main Streamlit UI
def run_pdf_summarizer():
    st.markdown("""
    <h1 style='color: #a970ff; font-family: "Segoe UI", sans-serif;'>AI-Powered PDF Summarizer</h1>
    <p style='color: #a970ff; font-size: 1.1rem; font-family: "Segoe UI", sans-serif;'>
    Upload a PDF and get crisp, AI-generated notes in seconds!</p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload your PDF", type=["pdf"])

    if uploaded_file:
        provider = st.session_state.get("llm_provider", "Offline / Local Mode (Free)")
        api_key = st.session_state.get("api_key") or os.getenv(f"{provider.upper()}_API_KEY")

        if provider != "Offline / Local Mode (Free)" and not api_key:
            st.warning(f"🔑 {provider} API Key is missing. Please provide it in the sidebar or select 'Offline / Local Mode (Free)' to run for free.")
            return

        try:
            st.info("⏳ Extracting text from PDF...")
            text = extract_text_from_pdf(uploaded_file)
            if not text.strip():
                st.error("❌ No readable text found in the PDF.")
                return

            text = clean_text(text)

            if provider == "Offline / Local Mode (Free)":
                st.info("⏳ Running local extractive summarizer...")
                final_summary = local_summarize(text)
            else:
                client = OpenAI(api_key=api_key) if provider == "OpenAI" else Groq(api_key=api_key)
                st.info(f"⏳ Querying {provider} to summarize your document...")
                chunks = chunk_text(text, 3000)
                st.markdown(f"📚 **Total chunks:** {len(chunks)} (each summarized separately)")
                summary_output = []

                progress = st.progress(0)
                for i, chunk in enumerate(chunks):
                    part_summary = summarize_chunk(chunk, client, provider)
                    summary_output.append(part_summary)
                    progress.progress((i + 1) / len(chunks))
                progress.empty()
                final_summary = "\n\n".join(summary_output)

            st.success("✅ Summary Generated!")
            st.markdown("<h3 style='color: #5e1f8c;'>📌 Summary:</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #5e1f8c; white-space: pre-wrap; font-family: Segoe UI;'>{final_summary}</div>", unsafe_allow_html=True)

            st.download_button(
                label="📥 Download Summary (.txt)",
                data=final_summary,
                file_name="summary_output.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

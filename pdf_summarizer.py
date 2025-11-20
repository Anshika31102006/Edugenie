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

# 🟣 Load OpenAI Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not found in .env file.")
    st.stop()

client = OpenAI(api_key=api_key)

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

# 🧠 Summarize one chunk using OpenAI
def summarize_chunk(chunk):
    prompt = f"""
    Summarize the following text into clear, concise bullet points focusing on key ideas, definitions, and facts.

    Text:
    {chunk}

    Return output as bullet points only, like:
    • Point 1
    • Point 2
    • Point 3
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # very fast + cost-efficient
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error summarizing chunk: {e}"

# 🚀 Main Streamlit UI
def run_pdf_summarizer():
    st.markdown("""
    <h1 style='color: #a970ff; font-family: "Segoe UI", sans-serif;'>AI-Powered PDF Summarizer</h1>
    <p style='color: #a970ff; font-size: 1.1rem; font-family: "Segoe UI", sans-serif;'>
    Upload a PDF and get crisp, AI-generated notes in seconds!</p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload your PDF", type=["pdf"])

    if uploaded_file:
        st.info("⏳ Extracting and summarizing your document...")

        try:
            text = extract_text_from_pdf(uploaded_file)
            if not text.strip():
                st.error("❌ No readable text found in the PDF.")
                return

            text = clean_text(text)
            chunks = chunk_text(text, 3000)

            st.markdown(f"📚 **Total chunks:** {len(chunks)} (each summarized separately)")
            summary_output = []

            progress = st.progress(0)
            for i, chunk in enumerate(chunks):
                part_summary = summarize_chunk(chunk)
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

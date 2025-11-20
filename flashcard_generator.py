# flashcard_generator.py
import streamlit as st
import time
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API keys
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Generate flashcards and quizzes
def generate_flashcards_and_quizzes(text):
    prompt = f"""
You are an AI learning assistant. Read the text below and generate:

- 5 flashcards in Q&A format
- 5 MCQs (each with 4 options labeled a–d and correct answer stated clearly)

Text:
\"\"\"{text}\"\"\"

Output format:
Q: (flashcard question)
A: (flashcard answer)

Q: (MCQ question)
a) ...
b) ...
c) ...
d) ...
Answer: (correct option letter)
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI learning assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# Streamlit UI
def run_flashcard_generator():
    st.markdown("<h1 style='color:#a970ff;'>🧠 Flashcard & Quiz Generator</h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload your study PDF", type=["pdf"])

    if uploaded_file is not None:
        st.success("✅ File uploaded successfully!")

        with st.spinner("🚀 Generating AI-powered Flashcards and Quizzes..."):
            try:
                pdf_text = extract_text_from_pdf(uploaded_file)
                result = generate_flashcards_and_quizzes(pdf_text)
                time.sleep(2)
                st.markdown("## 🔖 Flashcards & Quizzes Preview")
                st.markdown(f"<div style='color:black; white-space:pre-wrap;'>{result}</div>", unsafe_allow_html=True)
                st.success("🎉 Flashcards & Quizzes Generated!")
            except Exception as e:
                st.error(f"⚠️ Error generating flashcards: {e}")
    else:
        st.warning("⚠ Please upload a PDF file to get started.")

# Run if executed directly
if __name__ == "__main__":
    run_flashcard_generator()

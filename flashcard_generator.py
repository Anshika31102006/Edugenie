# flashcard_generator.py
import streamlit as st
import time
import fitz  # PyMuPDF
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from groq import Groq

load_dotenv()

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# Generate flashcards and quizzes using LLM
def generate_flashcards_and_quizzes(text, client, provider):
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

    model = "gpt-4o-mini" if provider == "OpenAI" else "llama-3.3-70b-versatile"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI learning assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

# 🧠 Local offline generator fallback
def local_generate_flashcards_and_quizzes(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    
    definitions = []
    for s in sentences:
        match = re.search(r'\b([A-Z][a-zA-Z\s]{3,25})\b\s+(is\s+defined\s+as|is\s+a|is|refers\s+to|means)\s+(.+)', s)
        if match:
            term = match.group(1).strip()
            defn = match.group(3).strip()
            if 10 < len(defn) < 150:
                definitions.append((term, defn))
                if len(definitions) >= 5:
                    break
                    
    if len(definitions) < 5:
        backup_terms = ["Learning Material", "Key Concept", "Important Topic", "Subject Study", "Revision Note"]
        for i, s in enumerate(sentences[:5]):
            if i < len(sentences):
                term = backup_terms[len(definitions)]
                definitions.append((term, s[:100] + "..."))
            if len(definitions) >= 5:
                break
                
    output_lines = []
    output_lines.append("### 🔖 Flashcards")
    for term, defn in definitions[:5]:
        output_lines.append(f"Q: What is the definition of **{term}**?")
        output_lines.append(f"A: {defn}\n")
        
    output_lines.append("### 🧠 Multiple Choice Questions")
    for term, defn in definitions[:5]:
        output_lines.append(f"Q: Which of the following describes **{term}**?")
        output_lines.append(f"a) {defn}")
        output_lines.append(f"b) A temporary storage system in system operations.")
        output_lines.append(f"c) A design methodology for building scalable microservices.")
        output_lines.append(f"d) None of the above.")
        output_lines.append("Answer: a\n")
        
    return "\n".join(output_lines)

# Parser to convert raw LLM output into python structures
def parse_flashcards_and_quizzes(text):
    flashcards = []
    quizzes = []
    
    sections = re.split(r'\n(?=Q:|Question:)', text)
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        lines = section.split('\n')
        question = ""
        answer = ""
        options = []
        is_mcq = False
        mcq_answer = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("Q:") or line.startswith("Question:"):
                question = re.sub(r'^(Q:|Question:)\s*', '', line).strip()
            elif line.startswith("A:") and not line.startswith("Answer:"):
                answer = re.sub(r'^A:\s*', '', line).strip()
            elif re.match(r'^[a-d][\)\.]', line):
                options.append(line)
                is_mcq = True
            elif line.startswith("Answer:") or line.startswith("Correct Answer:"):
                mcq_answer = re.sub(r'^(Answer:|Correct Answer:)\s*', '', line).strip().lower().replace(")", "").replace(".", "")
                is_mcq = True
                
        if question:
            if is_mcq:
                if options and mcq_answer:
                    quizzes.append((question, options, mcq_answer))
            else:
                if answer:
                    flashcards.append((question, answer))
                    
    return flashcards, quizzes

# Streamlit UI
def run_flashcard_generator():
    st.markdown("<h1 style='color:#a970ff;'>🧠 Flashcard & Quiz Generator</h1>", unsafe_allow_html=True)

    provider = st.session_state.get("llm_provider", "Offline / Local Mode (Free)")
    api_key = st.session_state.get("api_key") or os.getenv(f"{provider.upper()}_API_KEY")

    if provider != "Offline / Local Mode (Free)" and not api_key:
        st.warning(f"🔑 {provider} API Key is missing. Please provide it in the sidebar or select 'Offline / Local Mode (Free)' to run for free.")
        return

    uploaded_file = st.file_uploader("📄 Upload your study PDF", type=["pdf"])

    if uploaded_file is not None:
        # Check if a new file is uploaded to clear cache
        file_key = f"processed_{uploaded_file.name}"
        if file_key not in st.session_state:
            st.session_state[file_key] = None
            st.session_state.fc_index = 0
            st.session_state.fc_flipped = False

        if st.session_state[file_key] is None:
            with st.spinner("🚀 Extracting and generating quizzes..."):
                try:
                    pdf_text = extract_text_from_pdf(uploaded_file)
                    if provider == "Offline / Local Mode (Free)":
                        result_text = local_generate_flashcards_and_quizzes(pdf_text)
                    else:
                        client = OpenAI(api_key=api_key) if provider == "OpenAI" else Groq(api_key=api_key)
                        result_text = generate_flashcards_and_quizzes(pdf_text, client, provider)
                    
                    st.session_state[file_key] = result_text
                except Exception as e:
                    st.error(f"⚠️ Error during generation: {e}")
                    return

        # Load parsed items from session state
        result_text = st.session_state[file_key]
        flashcards, quizzes = parse_flashcards_and_quizzes(result_text)

        # ------------------------------
        # 🔖 Render Flashcards Tab/Section
        # ------------------------------
        if flashcards:
            st.markdown("## 🔖 Interactive Study Flashcards")
            
            if "fc_index" not in st.session_state:
                st.session_state.fc_index = 0
            if "fc_flipped" not in st.session_state:
                st.session_state.fc_flipped = False

            current_idx = st.session_state.fc_index
            if current_idx >= len(flashcards):
                current_idx = 0
                st.session_state.fc_index = 0
                
            q, a = flashcards[current_idx]
            
            card_side = "Answer 🔑" if st.session_state.fc_flipped else "Question ❓"
            card_text = a if st.session_state.fc_flipped else q
            
            card_html = f"""
            <div style="
                background: rgba(20, 20, 35, 0.65);
                border: 1px solid rgba(169, 112, 255, 0.25);
                border-radius: 16px;
                padding: 40px;
                text-align: center;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
                backdrop-filter: blur(8px);
                min-height: 180px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                margin-bottom: 20px;
            ">
                <h4 style="color: #00f0ff; margin-bottom: 10px; font-family: 'Outfit', sans-serif; letter-spacing: 1px;">{card_side}</h4>
                <p style="font-size: 1.35rem; font-weight: 500; color: #ffffff; font-family: 'Outfit', sans-serif; line-height: 1.5;">{card_text}</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("◀ Previous Card", use_container_width=True):
                    st.session_state.fc_index = (st.session_state.fc_index - 1) % len(flashcards)
                    st.session_state.fc_flipped = False
                    st.rerun()
            with col2:
                if st.button("🔄 Flip Card", use_container_width=True):
                    st.session_state.fc_flipped = not st.session_state.fc_flipped
                    st.rerun()
            with col3:
                if st.button("Next Card ▶", use_container_width=True):
                    st.session_state.fc_index = (st.session_state.fc_index + 1) % len(flashcards)
                    st.session_state.fc_flipped = False
                    st.rerun()
                    
            st.markdown(f"<p style='text-align:center; color:#00f0ff; font-weight: 600; font-family: Outfit, sans-serif;'>Card {current_idx + 1} of {len(flashcards)}</p>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ No flashcards could be parsed from the generated output.")

        st.markdown("---")

        # ------------------------------
        # 🧠 Render Quiz Section
        # ------------------------------
        if quizzes:
            st.markdown("## 🧠 Practice Quiz")
            user_answers = {}
            for idx, (q, opts, ans) in enumerate(quizzes):
                st.markdown(f"**Q{idx+1}: {q}**")
                selected_option = st.radio(
                    f"Choose option for question {idx+1}",
                    opts,
                    index=None,
                    key=f"mcq_{idx}",
                    label_visibility="collapsed"
                )
                user_answers[idx] = selected_option
                
            if st.button("📝 Submit Quiz", use_container_width=True):
                score = 0
                for idx, (q, opts, ans) in enumerate(quizzes):
                    user_ans = user_answers[idx]
                    user_letter = user_ans[0].lower() if user_ans else ""
                    correct_letter = ans.strip().lower()
                    
                    if user_letter == correct_letter:
                        score += 1
                        st.success(f"✔️ Question {idx+1}: Correct!")
                    else:
                        correct_opt_text = next((o for o in opts if o.lower().startswith(correct_letter)), correct_letter)
                        st.error(f"❌ Question {idx+1}: Incorrect. The correct answer was **{correct_opt_text}**.")
                        
                st.metric("Your Quiz Score", f"{score} / {len(quizzes)}")
                if score == len(quizzes):
                    st.balloons()
        else:
            st.warning("⚠️ No quizzes could be parsed from the generated output.")

    else:
        st.warning("⚠ Please upload a PDF file to get started.")

# Run if executed directly
if __name__ == "__main__":
    run_flashcard_generator()

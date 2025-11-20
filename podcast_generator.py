import streamlit as st
from PyPDF2 import PdfReader
from gtts import gTTS
import tempfile
import os
from dotenv import load_dotenv

# Load environment (optional for OpenAI fallback)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

try:
    from openai import OpenAI
    client = OpenAI(api_key=api_key) if api_key else None
except:
    client = None

# 🧠 Extract text from selected PDF pages
def extract_pdf_text(uploaded_file, selected_pages):
    reader = PdfReader(uploaded_file)
    text = ""
    for i in selected_pages:
        if 0 <= i < len(reader.pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# 🎧 Generate summarized text (optional)
def summarize_text(text):
    if not client:
        return text[:2000]  # fallback to first 2000 chars
    try:
        prompt = f"Summarize this for a spoken podcast under 250 words:\n{text[:6000]}"
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"⚠ Using full text due to summarization error: {e}")
        return text[:2000]

# 🎤 Generate TTS audio (offline and fast)
def generate_audio(text):
    try:
        tts = gTTS(text=text, lang="en", slow=False)
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_audio.name)
        return temp_audio.name
    except Exception as e:
        st.error(f"❌ TTS generation failed: {e}")
        return None

# 🚀 Streamlit Interface
def run_podcast_generator():
    st.markdown("""
    <h1 style='color: #a970ff; font-family: "Segoe UI", sans-serif;'>🎙 Podcast Generator</h1>
    <p style='color: #a970ff; font-size: 1.1rem;'>Convert your study PDFs into AI-narrated podcasts for quick revision.</p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📄 Upload your PDF here!", type=["pdf"])
    if not uploaded_file:
        return

    # Extract pages
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    st.markdown(f"🧾 This PDF has **{total_pages} pages**.")

    page_range = st.text_input("Enter page numbers (e.g., 1-3, 2, or all):", "all")
    if page_range.lower() == "all":
        selected_pages = list(range(total_pages))
    elif "-" in page_range:
        try:
            start, end = map(int, page_range.split("-"))
            selected_pages = list(range(start - 1, end))
        except:
            st.error("❌ Invalid page range.")
            return
    else:
        try:
            selected_pages = [int(page_range) - 1]
        except:
            st.error("❌ Invalid input.")
            return

    # Extract text
    full_text = extract_pdf_text(uploaded_file, selected_pages)
    if not full_text:
        st.error("❌ Could not extract any text.")
        return

    # Playback speed
    speed_label = st.select_slider(
        "🎚 Select Playback Speed",
        options=["0.75x", "1x", "1.5x", "2x", "2.5x", "3x"],
        value="1x"
    )
    speed_value = float(speed_label.replace("x", ""))

    st.text_area("📜 Text Preview", full_text[:1500] + "..." if len(full_text) > 1500 else full_text, height=250)

    if st.button("🎧 Generate & Play Podcast"):
        with st.spinner("🎙 Generating your podcast..."):
            summarized = summarize_text(full_text)
            audio_file = generate_audio(summarized)
            if not audio_file:
                return
            st.success("✅ Podcast Ready!")

            # Custom audio player with playback rate control
            audio_html = f"""
            <audio id="audioPlayer" controls>
                <source src="data:audio/mp3;base64,{open(audio_file, 'rb').read().encode('base64').decode()}" type="audio/mp3">
            </audio>
            <script>
                var audio = document.getElementById("audioPlayer");
                audio.playbackRate = {speed_value};
            </script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

            st.markdown("### 🗣 Podcast Script")
            st.markdown(f"<div style='white-space: pre-wrap; color:white;'>{summarized}</div>", unsafe_allow_html=True)

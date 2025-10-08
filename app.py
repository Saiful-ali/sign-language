import streamlit as st
import os
from PIL import Image
import speech_recognition as sr
from gtts import gTTS
import tempfile

# ---------------- Page Config ----------------
st.set_page_config(page_title="Language Helper", page_icon="🖐️", layout="centered")
st.title("🖐️ Language Helper")

# ---------------- Custom CSS ----------------
st.markdown(
    """
    <style>
    .title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #ff4c4c;
        animation: color-change 3s infinite;
    }
    @keyframes color-change {
        0% { color: #ff4c4c; }
        16% { color: #4cff4c; }
        33% { color: #4c4cff; }
        50% { color: #ff4cff; }
        66% { color: #ffff4c; }
        83% { color: #4cffff; }
        100% { color: #ff4c4c; }
    }
    .button-style {
        background-color: #393e46;
        color: #eeeeee;
        font-weight: bold;
        font-size: 20px;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        margin: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">Language Helper</div>', unsafe_allow_html=True)
st.markdown("## Choose Mode", unsafe_allow_html=True)

# ---------------- Session States ----------------
if 'constructed_text' not in st.session_state:
    st.session_state.constructed_text = ""

# ---------------- Columns for Mode Selection ----------------
col1, col2 = st.columns(2)

# ---------------- Audio → Sign ----------------
with col1:
    if st.button("Audio to Sign", key="audio_to_sign"):
        st.info("🎤 Listening for audio...")
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=5)
                recognized_text = recognizer.recognize_google(audio)
                st.success(f"✅ Recognized Text: {recognized_text}")

                # Display sign images
                st.subheader("Sign Representation")
                words = recognized_text.strip().split()
                for word in words:
                    cols = st.columns(len(word))
                    for i, char in enumerate(word):
                        if char.isalnum():
                            folder_path = os.path.join("Indian", char.upper())
                            if os.path.isdir(folder_path):
                                image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
                                if image_files:
                                    img_path = os.path.join(folder_path, image_files[0])
                                    img = Image.open(img_path).resize((120, 120))
                                    cols[i].image(img, caption=char.upper())
        except sr.WaitTimeoutError:
            st.error("Listening timed out. Please try again.")
        except sr.UnknownValueError:
            st.error("Could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"API Error: {e}")

# ---------------- Sign → Audio ----------------
with col2:
    st.subheader("Construct Text from Signs")
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cols_letters = st.columns(6)
    for i, letter in enumerate(letters):
        if cols_letters[i % 6].button(letter):
            st.session_state.constructed_text += letter

    st.text_area("Constructed Text", value=st.session_state.constructed_text, height=60)

    if st.button("🔊 Speak Text"):
        if st.session_state.constructed_text.strip():
            tts = gTTS(st.session_state.constructed_text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                st.audio(tmp_file.name, format="audio/mp3")
            os.remove(tmp_file.name)
        else:
            st.warning("Please construct some text first!")

    if st.button("❌ Clear Text"):
        st.session_state.constructed_text = ""
        st.experimental_rerun()

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("**Language Helper App** — Converts hand signs to audio and audio to hand signs")

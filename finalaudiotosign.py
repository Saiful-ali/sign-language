import streamlit as st
import speech_recognition as sr
from PIL import Image
import os
from gtts import gTTS
import tempfile

st.set_page_config(page_title="Audio ↔ Sign Language Translator", layout="wide")

st.title("🖐️ Audio ↔ Sign Language Translator")

# --- Audio → Sign ---
st.header("🎙️ Audio to Sign")

if st.button("Start Listening"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            st.info("🔍 Recognizing...")
            recognized_text = recognizer.recognize_google(audio)
            st.success(f"✅ Recognized: {recognized_text}")

            # Display signs
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

# --- Sign → Audio ---
st.header("🖐️ Sign to Audio")

# Constructed text
constructed_text = st.text_input("Constructed Text", value="")

# Alphabet buttons
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
cols = st.columns(6)
for i, letter in enumerate(letters):
    if cols[i % 6].button(letter):
        constructed_text += letter

st.text_area("Constructed Text", value=constructed_text, height=50)

if st.button("🔊 Speak"):
    if constructed_text.strip() == "":
        st.warning("Please construct text first!")
    else:
        # Convert text to speech using gTTS
        tts = gTTS(constructed_text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            st.audio(tmp_file.name, format="audio/mp3")

if st.button("❌ Clear Text"):
    constructed_text = ""
    st.experimental_rerun()

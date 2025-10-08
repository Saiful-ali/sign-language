import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
from PIL import Image
import os
from gtts import gTTS
import tempfile
import time

# ---------------- Page Config ----------------
st.set_page_config(page_title="Audio ↔ Sign Language Translator", layout="wide")
st.title("🖐️ Audio ↔ Sign Language Translator (Web + Webcam)")

# ---------------- Model Setup ----------------
@st.cache_resource
def load_models():
    try:
        base_dir = os.path.dirname(__file__)
        model_path = os.path.join(base_dir, "landmark_model.h5")
        encoder_path = os.path.join(base_dir, "label_encoder.pkl")
        model = load_model(model_path)
        encoder = joblib.load(encoder_path)
        return model, encoder
    except Exception as e:
        st.error(f"Error loading model or encoder: {e}")
        return None, None

model, encoder = load_models()
if model is None or encoder is None:
    st.stop()  # Stop app if models not loaded

# ---------------- Mediapipe Setup ----------------
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# ---------------- Functions ----------------
def extract_landmarks(image):
    rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    results = hands_detector.process(rgb)
    if not results.multi_hand_landmarks:
        return None

    all_landmarks = []
    for hand_landmarks in results.multi_hand_landmarks:
        for lm in hand_landmarks.landmark:
            all_landmarks.extend([lm.x, lm.y, lm.z])
    # Pad if only one hand
    if len(results.multi_hand_landmarks) == 1:
        all_landmarks.extend([0.0]*63)
    return np.array(all_landmarks).reshape(1, -1)

def predict_sign(image):
    landmarks = extract_landmarks(image)
    if landmarks is None:
        return None, None
    pred = model.predict(landmarks, verbose=0)
    confidence = np.max(pred)
    label = encoder.inverse_transform([np.argmax(pred)])[0]
    return (label, confidence) if confidence > 0.6 else (None, confidence)

def display_sign_images(label):
    folder_path = os.path.join("sign_images", label)
    if not os.path.isdir(folder_path):
        st.warning(f"No folder found for label: {label}")
        return
    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith((".jpg",".png"))])
    if not image_files:
        st.warning(f"No images found for label: {label}")
        return
    cols = st.columns(len(image_files))
    for i, img_file in enumerate(image_files):
        img_path = os.path.join(folder_path, img_file)
        img = Image.open(img_path).resize((120,120))
        cols[i].image(img, caption=img_file.split(".")[0])

def text_to_speech(text):
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        st.audio(tmp_file.name, format="audio/mp3")
    os.remove(tmp_file.name)

# ---------------- Webcam Input ----------------
st.header("📸 Live Webcam Sign Recognition")
if 'last_label' not in st.session_state:
    st.session_state.last_label = ""

cam_file = st.camera_input("Take a snapshot to detect hand signs")
if cam_file:
    image = Image.open(cam_file).convert("RGB")
    st.image(image, caption="Captured Frame", use_column_width=True)

    label, confidence = predict_sign(image)
    if label:
        st.success(f"✅ Recognized Sign: {label} (Confidence: {confidence*100:.1f}%)")
        st.session_state.last_label = label
        display_sign_images(label)
        if st.button("🔊 Speak Recognized Sign"):
            text_to_speech(label)
    else:
        st.warning(f"Could not recognize the sign. Confidence: {confidence*100:.1f}%")
        st.info("Ensure hands are clearly visible and inside the camera frame.")

st.info("Tip: Take multiple snapshots to simulate live detection.")

# ---------------- Constructed Text Section ----------------
st.header("✍️ Sign to Audio")
if 'constructed_text' not in st.session_state:
    st.session_state.constructed_text = ""

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
cols = st.columns(6)
for i, letter in enumerate(letters):
    if cols[i % 6].button(letter):
        st.session_state.constructed_text += letter

st.text_area("Constructed Text", value=st.session_state.constructed_text, height=60)
if st.button("🔊 Speak Text"):
    if st.session_state.constructed_text.strip():
        text_to_speech(st.session_state.constructed_text)
    else:
        st.warning("Please construct some text first!")

if st.button("❌ Clear Text"):
    st.session_state.constructed_text = ""

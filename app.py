import streamlit as st
import time
# Set page configuration
st.set_page_config(page_title="Language Helper", page_icon="🖐️", layout="centered")

# Custom CSS for colors and styles
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

# Animated title
st.markdown('<div class="title">Language Helper</div>', unsafe_allow_html=True)
st.markdown("## Choose Mode", unsafe_allow_html=True)

# Layout buttons in two columns
col1, col2 = st.columns(2)

with col1:
    if st.button("Audio to Sign", key="audio_to_sign"):
        st.info("Processing Audio to Sign...")
        try:
            run_audio_to_sign_main()
            st.success("Audio to Sign conversion completed!")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("Sign to Audio", key="sign_to_audio"):
        st.info("Processing Sign to Audio...")
        try:
            run_sign_to_audio_main()
            st.success("Sign to Audio conversion completed!")
        except Exception as e:
            st.error(f"Error: {e}")

# Footer or extra info
st.markdown("---")
st.markdown("**Language Helper App** — Converts hand signs to audio and audio to hand signs")

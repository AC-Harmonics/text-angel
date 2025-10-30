import streamlit as st
st.set_page_config("TEXT ANGEL: Welcome", layout="centered")
from avatar_builder import build_avatar
from PIL import Image
import json
from pathlib import Path

def get_user_profile():
    profile_path = Path("data/user_profile.json")
    if profile_path.exists():
        with open(profile_path) as f:
            return json.load(f)
    else:
        return {
            "username": "Unknown",
            "guardian_name": "Angel",
            "avatar": "😇",
            "tone_default": "GRACE"
        }
    
st.title("👼 Welcome to TEXT ANGEL")

# === Account Info ===
st.header("🔐 Create Your Account")
username = st.text_input("Choose your Username")
guardian = st.text_input("Name Your Guardian Angel")

# === Avatar Section ===
st.header("🧝‍♀️ Build Your Avatar")

base_map = {"Flame": "Flame", "Guardian": "Guardian", "Oracle": "Oracle"}
halo_map = {"Gold": "Gold", "Mint": "Mint", "Blue": "Blue"}
aura_map = {"None": None, "Gold": "Gold", "Blue": "Blue"}
face_map = {"None": None, "🙂": "🙂"}

base_choice = st.selectbox("Choose Avatar Type", list(base_map.keys()))
halo_color = st.radio("Choose Halo Color", list(halo_map.keys()))
aura = st.radio("Select Aura Glow", list(aura_map.keys()))
accessory = st.checkbox("✨ Add Star Accessory")
face_emoji = st.selectbox("Choose Your Face Style", list(face_map.keys()))

avatar = build_avatar(
    base_choice,
    halo_color,
    aura,
    accessory,
    face_emoji=face_emoji if face_emoji != "None" else None
)

st.image(avatar, caption="Your Avatar Preview", use_column_width=True)

# === Tone Default Setup ===
st.header("🎨 Select Your Default Message Tone")
tone_default = st.radio("Choose a tone: ", ["None", "GRACE", "TRUTH", "CALM"])

if tone_default == "GRACE":
    st.info("🌸 GRACE will soften your messages into kind, gentle tone.")
elif tone_default == "TRUTH":
    st.info("🪞 TRUTH keeps messages honest, clear, and respectful.")
elif tone_default == "CALM":
    st.info("🙷 CALM rewrites messages to be emotionally grounded.")
else:
    st.info("✍️ Original tone will be preserved.")

# === Finalize Setup ===
if st.button("✅ Complete Setup"):
    st.session_state.username = username
    st.session_state.guardian_name = guardian
    st.session_state.base_choice = base_choice
    st.session_state.halo_color = halo_color
    st.session_state.aura = aura
    st.session_state.accessory = accessory
    st.session_state.face_emoji = face_emoji
    st.session_state.tone_default = tone_default
    st.session_state.avatar_image = avatar
    st.session_state.setup_complete = True

    st.success("Account Created! Entering Unified Mode...")
    st.switch_page("text angel unified")  # 👈 Corrected here







import streamlit as st
import json
from pathlib import Path
import os

from avatar_builder import build_avatar, save_avatar_image, get_avatar_url

# --- Page Config ---
st.set_page_config(page_title="TEXT ANGEL – Welcome", layout="centered")

# --- Constants ---
PROFILE_PATH = Path("data/user_profile.json")
AVATAR_ID = "d"  # TODO: make dynamic per user/session later
avatars = ["😇", "🛡️", "💖", "🦋", "🌟", "🎵", "👼"]
tones = {
    "GRACE": "Gentle, kind, nurturing",
    "TRUTH": "Honest, clear, direct",
    "CALM": "Peaceful, grounded, safe"
}

# --- Load saved profile (if exists) ---
if PROFILE_PATH.exists():
    with open(PROFILE_PATH) as f:
        user_profile = json.load(f)
    st.session_state.update(user_profile)

# --- UI Header ---
st.title("🎨 Create Your TEXT ANGEL Avatar")

# === Avatar Builder Form ===
base = st.selectbox("Choose your Avatar Type", ["Flame", "Guardian", "Oracle"])
halo = st.radio("Choose your Halo Color", ["Gold", "Mint", "Blue"])
aura = st.radio("Select Aura Glow", ["None", "Gold", "Blue"])
face = st.selectbox("Choose Your Face", ["🙂"])
accessory = st.checkbox("Add Star Accessory")

if st.button("Enter the Flame Portal"):
    avatar_img = build_avatar(base, halo, aura, accessory=accessory, face_emoji=face)
    save_avatar_image(avatar_img, user_id=AVATAR_ID)
    st.success("✨ Your Avatar has been generated!")

    avatar_url = get_avatar_url(AVATAR_ID)
    st.image(avatar_url, caption="Your Avatar Preview", width=200)

st.markdown("---")

# === Profile Input ===
st.title("😇 Welcome to TEXT ANGEL")
st.markdown("Your harmonic guardian for safe, kind, and emotionally aware messaging.")

username = st.text_input("What is your name?")
guardian_name = st.text_input("Choose a Guardian Angel name (e.g., Seraphiel, Lumi, Zerah):")
avatar_icon = st.selectbox("Pick your Guardian Emoji:", avatars)
tone_default = st.selectbox("Choose your Power Tone:", list(tones.keys()), format_func=lambda x: f"{x} — {tones[x]}")

# --- Save Profile + Redirect ---
if st.button("✨ Enter the Angel Portal ✨"):
    if username.strip() == "" or guardian_name.strip() == "":
        st.warning("Please fill in both your name and guardian name.")
    else:
        profile = {
            "username": username,
            "guardian_name": guardian_name,
            "avatar": avatar_icon,
            "tone_default": tone_default
        }
        PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PROFILE_PATH, "w") as f:
            json.dump(profile, f)

        st.success("Profile saved!")
        st.switch_page("pages/text_angel_UI.py")  # Or your page name

import streamlit as st
import os
import sys
from PIL import Image
import openai.error
import json, re
import openai
from pathlib import Path
import time
from dotenv import load_dotenv

        
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Fix path so you can import from parent directory ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# === INITIALIZATION ===
st.set_page_config(page_title="TEXT ANGEL Unified", layout="centered")

if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False

from avatar_builder import build_avatar
from log_scroll_and_badge_engine import log_to_scroll
from profile_system import (
    load_user_profile,
    update_profile_field,
    get_tone_default,
    add_badge
)

# === AVATAR IMAGE MAPS ===
base_map = {
    "Flame": "assets/avatars/base_flame.png",
    "Guardian": "assets/avatars/base_guardian.png",
    "Oracle": "assets/avatars/base_oracle.png"
}
halo_map = {
    "Gold": "assets/avatars/halo_gold.png",
    "Mint": "assets/avatars/halo_mint.png",
    "Blue": "assets/avatars/halo_blue.png"
}
aura_map = {
    "Gold": "assets/avatars/aura_gold.png",
    "Blue": "assets/avatars/aura_blue.png"
}
accessory_path = "assets/avatars/accessory_star.png"

# === WELCOME SCREEN ===
if not st.session_state.welcome_shown:
    st.title("🎨 Create Your TEXT ANGEL Avatar")

    base_choice = st.selectbox("Choose your Avatar Type", list(base_map.keys()))
    halo_color = st.radio("Choose your Halo Color", list(halo_map.keys()))
    aura = st.radio("Select Aura Glow", ["None"] + list(aura_map.keys()))
    accessory = st.checkbox("✨ Add Star Accessory")
    face_emoji = st.selectbox("Choose Your Face", ["None", "😊"])

    avatar = build_avatar(
        base_choice,
        halo_color,
        aura,
        accessory,
        face_emoji=face_emoji if face_emoji != "None" else None
    )

    st.image(avatar, caption="Your Avatar Preview")

    if st.button("Enter the Flame Portal"):
        st.session_state.base_choice = base_choice
        st.session_state.halo_color = halo_color
        st.session_state.aura = aura
        st.session_state.accessory = accessory
        st.session_state.face_emoji = face_emoji
        st.session_state.avatar_image = avatar
        st.session_state.welcome_shown = True
        st.rerun()

    st.stop()

# === SESSION SETUP ===
base_choice = st.session_state.base_choice
halo_color = st.session_state.halo_color
aura = st.session_state.aura
accessory = st.session_state.accessory
face_emoji = st.session_state.face_emoji
avatar_image = st.session_state.avatar_image

st.image(avatar_image, caption="Your TEXT ANGEL Avatar", use_container_width=True)

# === AVATAR EMOJI OPTIONS ===
avatar_options = {
    "🕊️": "Peace Dove",
    "🌈": "Rainbow Flame",
    "🛡️": "Guardian Shield",
    "💎": "Crystal Voice",
    "🔥": "Flame Oracle"
}

# === LOAD USER PROFILE ===
user_profile = load_user_profile()
username = user_profile["username"]
guardian = user_profile["guardian_name"]
avatar = user_profile["avatar"]
tone_default = get_tone_default()

# === SIDEBAR DISPLAY ===
st.sidebar.header(f"{avatar} Welcome, {username}!")
st.sidebar.markdown(f"**Guardian Angel:** {guardian}")
selected_default = st.sidebar.selectbox(
    "Choose your default tone",
    ["GRACE", "TRUTH", "CALM"],
    index=["GRACE", "TRUTH", "CALM"].index(tone_default),
    key="tone_selector"
)

# === SHIELD FILTER ===
with open("shield_filter_words.json", "r") as f:
    shield_words = json.load(f)

# === HELPER: CENSOR ===
def censor_message(message, shield_list):
    blocked_count = 0
    censored_message = message
    for word in shield_list:
        word_pattern = re.compile(r'\b' + re.escape(word) + r'\b', flags=re.IGNORECASE)
        if word_pattern.search(censored_message):
            blocked_count += len(word_pattern.findall(censored_message))
            censored_message = word_pattern.sub("▆▆▆", censored_message)
    return censored_message, blocked_count

# === HELPER: TONE REWRITER ===
def rewrite_with_tone(message, tone):
    if tone == "None":
        return message  # No rewrite, return original

    prompt_map = {
        "GRACE": "Rewrite this to be kind, nurturing, and soft:",
        "TRUTH": "Rewrite this to be honest and respectful:",
        "CALM": "Rewrite this to be peaceful, grounded, and emotionally safe:"
    }

    fallback = "Rewrite this message with empathy"
    prompt_text = prompt_map.get(tone, fallback)
    prompt = f"{prompt_text}\n\nOriginal: {message}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a message tone transformer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message["content"].strip()

# === MAIN VIEW ===
st.title("😇 TEXT ANGEL – Unified Guardian Mode")

# === OUTGOING MESSAGE REWRITE ===
st.header("📝 Rewrite a Message")
tone = st.selectbox("Choose a tone:", ["None", "GRACE", "TRUTH", "CALM"])
user_message = st.text_area("What do you want to say?", key="rewrite")

if user_message:
    rewritten = rewrite_with_tone(user_message, tone)
    st.success(f"✅ Message rewritten with {tone}:")
    st.markdown(f"**Output:**\n\n{rewritten}")
    log_to_scroll(user=username, tone=tone, original=user_message, rewritten=rewritten, shielded_count=0)

st.divider()

# === INCOMING MESSAGE SHIELD ===
st.header("🛡️ Shield an Incoming Message")
incoming_message = st.text_area("📥 Paste the message you received:", height=200, key="incoming")

if incoming_message:
    censored, blocked_count = censor_message(incoming_message, shield_words)

    if blocked_count > 0:
        st.error("⚠️ This message was shielded by TEXT ANGEL.")
        st.markdown(f'''
        <div style='background-color:#FFF0F0; padding:1em; border-radius:10px; border: 1px solid red;'>
            📯 <b>Shielded Message:</b><br>
            <i>{censored}</i><br><br>
            <b>{blocked_count} word{'s' if blocked_count > 1 else ''} were shielded.</b><br>
            <b>🕊️ Guardian: {guardian}</b>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.success("✅ This message contains no harmful words.")

    log_to_scroll(user=username, tone="SHIELD", original=incoming_message, rewritten=censored, shielded_count=blocked_count)

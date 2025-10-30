import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import datetime
from angel_edit_engine import handle_rewrite_input, shield_input_text
from avatar_builder import get_avatar_url
from home_setup import get_user_profile

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    textarea, .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #d0e0f0;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- PROFILE ----
user_profile = get_user_profile()
avatar_url = get_avatar_url(user_profile.get('username', 'default'))

st.markdown(f"""
<div style="text-align: center;">
    <img src="{avatar_url}" width="180" style="border-radius: 50%; box-shadow: 0 0 20px gold;">
    <p style="margin-top: -10px; font-style: italic; font-size: 14px;">{user_profile['username']} – Your TEXT ANGEL Avatar</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---- TONE SELECTOR ----
st.markdown("### 💫 Choose Your Power Tone")
tone = st.selectbox("Which tone would you like your Angel to use?", ["GRACE", "TRUTH", "CALM"])
st.markdown("*Choose the tone your angel would speak with.* 💬")

st.markdown("---")

# ---- REWRITE MODE ----
st.markdown("### 😇 Rewrite a Message")
user_input = st.text_area("Type what you want to say...", height=150)
if st.button("Rewrite with Love ✨"):
    if user_input:
        rewritten, shield_count = handle_rewrite_input(tone, user_input)

        # Display Rewritten Message
        st.markdown(f"""
        <div style="background-color: #fef9f3; border-radius: 12px; padding: 15px; border: 2px solid #f4d2a5;">
            <p style="font-size: 16px;">✨ <b>TEXT ANGEL says:</b></p>
            <p style="font-size: 18px; font-style: italic;">\"{rewritten}\"</p>
        </div>
        """, unsafe_allow_html=True)

        # Play Sound
        st.audio("assets/sounds/angel_bell.ogg", autoplay=True)

        # Shield Info
        if shield_count > 0:
            st.warning(f"⚠️ {shield_count} word{'s' if shield_count > 1 else ''} were shielded by TEXT ANGEL.")

        # Log
        with open("data/message_log.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} | {user_profile['username']} | {tone}\n{user_input} => {rewritten}\n\n")
st.markdown("---")

# ---- SHIELD MODE ----
st.markdown("### 🛡 Shield an Incoming Message")
shield_input = st.text_area("Paste a message someone sent you that felt hurtful or unsafe:", key="shield")
if st.button("Protect Me 🕊️"):
    shielded, count = shield_input_text(shield_input)
    if shielded:
        st.markdown(f"""
        <div style="background-color: #f3f9f9; border-radius: 12px; padding: 15px; border: 2px solid #b5e0ea;">
            <p><b>Shielded Message:</b></p>
            <p style="font-size: 18px;">{shielded}</p>
        </div>
        """, unsafe_allow_html=True)
        st.info(f"⚠️ {count} word{'s' if count > 1 else ''} were shielded by TEXT ANGEL.")

st.markdown("---")

# ---- BADGE PREVIEW ----
st.markdown("### 🏆 Achievements Preview")
st.markdown("🌈 Kindness Flame Lv. 1 — after 10 gentle rewrites")
st.markdown("🗡️ Guardian Angel Lv. 2 — after shielding 25 words")

st.markdown("---")

# ---- FOOTER ----
st.markdown("<p style='text-align: center; font-size: 13px;'>Made with 💖 by AetherCode Genova · TEXT ANGEL v1.1</p>", unsafe_allow_html=True)

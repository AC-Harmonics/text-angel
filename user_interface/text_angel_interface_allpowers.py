import streamlit as st
import openai
import os
import json
from datetime import datetime
import uuid
import re

# --- PAGE SETUP --- #
st.set_page_config(page_title="TEXT ANGEL", page_icon="😇")

# --- CONFIG --- #
SOUND_FILE = "https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg"
LOG_PATH = "data/message_log.txt"
SHIELD_WORDS_PATH = os.path.join(os.path.dirname(__file__), "..", "shield_filter", "shield_filter_words.json")

try:
    with open(SHIELD_WORDS_PATH) as f:
        shield_words = json.load(f)
except FileNotFoundError:
    shield_words = []
    st.warning("Shield words file not found. Running without filter.")

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Tone Styles --- #
tone_styles = {
    "GRACE": {"color": "#FFF9E6", "emoji": "💛"},
    "TRUTH": {"color": "#E6F0FF", "emoji": "💙"},
    "CALM": {"color": "#E6FFF0", "emoji": "💚"}
}

# --- Tone Prompts --- #
tone_prompts = {
    "GRACE": "Rewrite this message with gentle kindness, compassion, and loving understanding:",
    "TRUTH": "Rewrite this message with honest clarity, directness, and truth but not cruelty:",
    "CALM": "Rewrite this message to sound calm, peaceful, and emotionally soothing:"
}

st.title("😇 TEXT ANGEL")
st.subheader("Fix your message with Grace, Truth, or Calm.")

# --- PROFILE --- #
st.markdown("### 👤 Your Profile")
username = st.text_input("Your name:", value="Jagger")
avatar = st.selectbox("Choose your angel avatar:", ["😇", "🧚", "🕊️", "🛡️", "🌟"])
default_tone = st.selectbox("Choose your favorite Angel Tone:", ["GRACE", "TRUTH", "CALM"])
style_pref = st.selectbox("Your messaging style:", ["Direct", "Gentle", "Playful", "Quiet"])
triggers = st.multiselect("Common triggers (optional):", ["Criticism", "Sarcasm", "Being ignored", "Too many messages"])
guardian = st.text_input("Name your Guardian Angel (just for fun):", value="Seraphiel")
reminder = st.text_input("Reminder before sending:", value="Speak like an angel")
auto_filter = st.slider("Auto-Filter Sensitivity", 0, 10, 7)

st.markdown("---")

# --- MAIN --- #
message = st.text_area("📨 Type your message:", height=150)
tone = st.selectbox("🧭 Choose an Angel Tone for this message:", ["GRACE", "TRUTH", "CALM"], index=["GRACE", "TRUTH", "CALM"].index(default_tone))
submit = st.button("🕊️ Angel Edit")

# --- Utilities --- #
def log_message(user, tone, original, rewritten):
    os.makedirs("data", exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now()}] {user} | Tone: {tone}\nOriginal: {original}\nFiltered: {rewritten}\n\n")

def censor_message(message, blocked_words):
    count = 0
    censored = message
    for word in blocked_words:
        pattern = r'\b' + re.escape(word) + r'\b'
        matches = re.findall(pattern, censored, flags=re.IGNORECASE)
        if matches:
            count += len(matches)
            censored = re.sub(pattern, '▆▆▆', censored, flags=re.IGNORECASE)
    return censored, count

# --- PROCESS --- #
if submit and message:
    st.caption(f"🧘 {reminder}")
    censored_message, shield_count = censor_message(message, shield_words)

    with st.spinner("Calling your angel..."):
        try:
            prompt = f"{tone_prompts[tone]} {censored_message}"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a kind and emotionally intelligent assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            rewritten = response["choices"][0]["message"]["content"]
            style = tone_styles[tone]

            st.success("✅ Your message has been filtered!")
            st.audio(SOUND_FILE)

            st.markdown(f"""
                <div style='background-color: {style["color"]}; padding: 1em; border-radius: 10px;'>
                    <b>{style["emoji"]} Here's your message rewritten with {tone.title()}:</b><br><br>
                    <i>{rewritten}</i>
                </div>
            """, unsafe_allow_html=True)

            if shield_count > 0:
                st.info(f"⚠️ {shield_count} word{'s' if shield_count > 1 else ''} were shielded by TEXT ANGEL.")

            log_message(username, tone, message, censored_message)

        except Exception as e:
            st.error(f"Error: {e}")

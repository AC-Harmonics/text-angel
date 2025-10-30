import streamlit as st
import openai
import os
from datetime import datetime

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Angel tone prompts
tone_prompts = {
    "GRACE": "Rewrite the following message with kindness, care, and gentleness.",
    "TRUTH": "Rewrite the following message to be honest, clear, and respectful.",
    "CALM": "Rewrite the following message in a peaceful and soft tone, with no harshness."
}

# Tone colors and emojis
tone_styles = {
    "GRACE": {"color": "#FFF9E6", "emoji": "💛"},
    "TRUTH": {"color": "#E6F0FF", "emoji": "💙"},
    "CALM": {"color": "#E6FFF0", "emoji": "💚"}
}

st.set_page_config(page_title="TEXT ANGEL", page_icon="😇")
st.title("😇 TEXT ANGEL")
st.subheader("Fix your message with Grace, Truth, or Calm.")

# Input
message = st.text_area("Type your message below:", height=150)
tone = st.selectbox("Choose an Angel Tone:", ["GRACE", "TRUTH", "CALM"])
submit = st.button("🕊️ Angel Edit")

# Process
if submit and message:
    with st.spinner("Calling your angel..."):
        try:
            prompt = f"{tone_prompts[tone]} Message: {message}"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a kind and emotionally intelligent assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            rewritten = response['choices'][0]['message']['content']
            style = tone_styles[tone]

            # Display styled output
            st.markdown(f"""
                <div style='background-color: {style["color"]}; padding: 1em; border-radius: 10px;'>
                    <b>{style["emoji"]} Here's your message rewritten with {tone.title()}:</b><br><br>
                    <i>{rewritten}</i>
                </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")

"""Angel Edit Engine – core rewriting logic for TEXT ANGEL.

This module powers both the Streamlit front-end and CLI version.
It rewrites user messages in graceful, honest, or calm tones,
filtering harmful or harsh expressions before sending to OpenAI.
"""

from __future__ import annotations
import os
import openai


# ---------------------------------------------------------------------
#  🔑 API Configuration
# ---------------------------------------------------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Please set it in your environment before running Text Angel."
    )

client = openai.OpenAI(api_key=api_key)


# ---------------------------------------------------------------------
#  🎵 Tone Instructions
# ---------------------------------------------------------------------
TONE_PROMPTS = {
    "GRACE": "Rewrite the following message with kindness, care, and gentleness.",
    "TRUTH": "Rewrite the following message to be honest, clear, and respectful.",
    "CALM": "Rewrite the following message in a peaceful and soft tone, with no harshness.",
}


# ---------------------------------------------------------------------
#  🛡️ Shield Input Text
# ---------------------------------------------------------------------
def shield_input_text(message: str) -> str:
    """Block or warn about harmful words before rewriting."""
    blocked_terms = ["hate", "stupid", "kill", "dumb", "ugly", "idiot", "worthless"]

    if any(term in message.lower() for term in blocked_terms):
        return (
            "⚠️ Message contained harmful or aggressive words. "
            "Please rephrase kindly before rewriting."
        )

    return message.strip()


# ---------------------------------------------------------------------
#  🪽 Handle Rewrite Input
# ---------------------------------------------------------------------
def handle_rewrite_input(message: str, tone: str = "GRACE") -> str:
    """Rewrite a message using the specified tone."""
    if tone not in TONE_PROMPTS:
        raise ValueError("Invalid tone. Choose from GRACE, TRUTH, or CALM.")

    if not message.strip():
        raise ValueError("Message cannot be empty.")

    prompt = f"{TONE_PROMPTS[tone]} Message: {message.strip()}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a kind and emotionally intelligent assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=150,
    )

    rewritten = response.choices[0].message.content.strip()
    return rewritten


# ---------------------------------------------------------------------
#  🧠 Core Engine
# ---------------------------------------------------------------------
def angel_edit(message: str, tone: str = "GRACE") -> str:
    """Main wrapper combining shield + rewrite."""
    safe_text = shield_input_text(message)

    if safe_text.startswith("⚠️"):
        return safe_text

    return handle_rewrite_input(safe_text, tone)


# ---------------------------------------------------------------------
#  💻 Command-Line Interface
# ---------------------------------------------------------------------
def main() -> None:
    """Run Text Angel interactively in the terminal."""
    print("\n🪽 Welcome to TEXT ANGEL – Angel Edit Engine 🕊️")
    message = input("Type your message: ").strip()
    tone = input("Choose a tone (GRACE, TRUTH, CALM): ").strip().upper()

    try:
        rewritten = angel_edit(message, tone)
        print(f"\n✨ Rewritten Message ({tone}) ✨\n{rewritten}\n")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

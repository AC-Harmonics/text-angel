"""Angel Edit Engine – core rewriting logic for TEXT ANGEL."""

from __future__ import annotations
import os
import openai

# Configure the OpenAI client using the environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable not set.")
client = openai.OpenAI(api_key=api_key)

# Tone instructions
TONE_PROMPTS = {
    "GRACE": "Rewrite the following message with kindness, care, and gentleness.",
    "TRUTH": "Rewrite the following message to be honest, clear, and respectful.",
    "CALM": "Rewrite the following message in a peaceful and soft tone, with no harshness.",
}

# ---------------------------------------------------------------------
# Main Rewrite Function
# ---------------------------------------------------------------------
def handle_rewrite_input(message: str, tone: str = "GRACE") -> str:
    """Rewrites the input message using the chosen tone."""
    if tone not in TONE_PROMPTS:
        raise ValueError("Invalid tone. Choose from GRACE, TRUTH, or CALM.")

    prompt = f"{TONE_PROMPTS[tone]} Message: {message}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a kind and emotionally intelligent assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=150,
    )

    return response.choices[0].message.content.strip()

# ---------------------------------------------------------------------
# Shield Filter Function
# ---------------------------------------------------------------------
def shield_input_text(message: str) -> str:
    """Simple text shield – blocks harmful or aggressive phrases before rewrite."""
    blocked_terms = ["hate", "stupid", "kill", "dumb", "ugly"]
    if any(term in message.lower() for term in blocked_terms):
        return "⚠️ Message contained harmful words. Please rephrase kindly."
    return message

# ---------------------------------------------------------------------
# CLI Test Mode
# ---------------------------------------------------------------------
def main() -> None:
    """Run interactively from terminal."""
    print("🕊️ TEXT ANGEL – Angel Edit Engine\n")
    msg = input("Type your message: ")
    tone = input("Choose a tone (GRACE, TRUTH, CALM): ").strip().upper()

    safe_text = shield_input_text(msg)
    if safe_text.startswith("⚠️"):
        print(safe_text)
        return

    try:
        rewritten = handle_rewrite_input(safe_text, tone)
        print(f"\nRewritten Message ({tone}):\n{rewritten}")
    except Exception as exc:
        print(f"Error: {exc}")

if __name__ == "__main__":
    main()

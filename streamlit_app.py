"""Streamlit front-end for the Text Angel protective writing assistant."""

import streamlit as st
from text_angel.angel_edit_engine import handle_rewrite_input, shield_input_text

APP_TITLE = "🪽 Text Angel | Protective Messaging"


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🪽", layout="centered")
    st.title(APP_TITLE)
    st.write(
        "Text Angel shields sensitive language and offers tone rewrites so conversations "
        "stay kind, professional, and emotionally safe."
    )

    st.markdown("---")

    # --- Sidebar Controls ---
    st.sidebar.header("Angel Settings")
    tone = st.sidebar.radio(
        "Choose your rewrite tone:",
        ["GRACE", "TRUTH", "CALM"],
        help="GRACE = gentle & kind, TRUTH = clear & honest, CALM = soft & peaceful",
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Your message will be checked for harmful words before rewriting. "
        "Uses your live OpenAI key from environment variables."
    )

    # --- Input Area ---
    st.subheader("💬 Write or paste a message:")
    user_message = st.text_area(
        "Message to rewrite:",
        placeholder="Type something that needs a little more care...",
        height=150,
    )

    if st.button("🕊️ Shield & Rewrite Message"):
        if not user_message.strip():
            st.warning("Please enter a message first.")
            return

        # Step 1 – run through shield
        safe_text = shield_input_text(user_message)
        if safe_text.startswith("⚠️"):
            st.error(safe_text)
            return

        # Step 2 – rewrite with selected tone
        with st.spinner("Rewriting with your selected tone..."):
            try:
                rewritten = handle_rewrite_input(safe_text, tone)
                st.success("✨ Message rewritten successfully!")
                st.markdown(f"**Tone applied:** {tone}")
                st.text_area("Rewritten Message:", rewritten, height=200)
            except Exception as e:
                st.error(f"Error during rewrite: {e}")

    st.markdown("---")
    st.caption("🪽 Built with love for kind communication – Text Angel")


if __name__ == "__main__":
    main()

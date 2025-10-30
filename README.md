# 🪽 Text Angel

Text Angel is a protective writing assistant that shields harmful language and rewrites
messages into caring, professional, or empathetic tones. The Streamlit front-end in this
repository mirrors the core workflow described in `text_angel_briefing.txt` and can be run
locally or deployed to Streamlit Cloud for rapid demos.

## Features

- 🛡️ **Shield filtering** – configurable word lists grouped by category, with support for
  custom additions at runtime.
- 🎚️ **Tone rewrites** – local templates that transform the shielded text into four
  selectable tones (Gentle & Kind, Professional, Empathetic, Calm & Direct).
- 📊 **Safety dashboard** – highlights of shield activity, category counts, and rewritten
  guidance so caregivers can quickly assess a message.

## Getting started

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit experience**

   ```bash
   streamlit run streamlit_app.py
   ```

3. **(Optional) Connect to the hosted API**

   The local tone rewrites are template-based to keep this repository self-contained. If
   you have access to the GPT-powered FastAPI backend mentioned in the project briefing,
   update the Streamlit app to call your endpoint instead of the local templates.

## Tests

Unit tests cover the shielding and tone transformation helpers. Run them with:

```bash
pytest
```

## Assets

- `shield_filter_words.json` – default categories and phrases used by the shield filter.
- `text_angel_briefing.txt` – high-level product background and future roadmap.

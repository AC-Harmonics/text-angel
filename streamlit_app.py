"""Streamlit front-end for the Text Angel protective writing assistant."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import streamlit as st

from text_angel import (
    AVAILABLE_TONES,
    RewriteResult,
    ShieldConfig,
    ShieldResult,
    ShieldingError,
    load_shield_config,
    rewrite_text,
    shield_text,
)

APP_TITLE = "🪽 Text Angel | Protective Messaging"
SHIELD_PATH = Path(__file__).parent / "shield_filter_words.json"


@st.cache_data(show_spinner=False)
def load_config(path: Path) -> ShieldConfig:
    return load_shield_config(path)


def build_active_config(base: ShieldConfig, categories: List[str], custom_words: List[str]) -> ShieldConfig:
    selected_categories: Dict[str, List[str]] = {
        category: list(base.categories[category])
        for category in categories
        if category in base.categories
    }
    if custom_words:
        selected_categories["custom"] = sorted({word.strip() for word in custom_words if word.strip()})
    if not selected_categories:
        selected_categories = {
            category: list(words) for category, words in base.categories.items()
        }
    return ShieldConfig(categories=selected_categories, replacement=base.replacement)


@dataclass
class AppState:
    tone_label: str
    extra_words: List[str]
    active_categories: List[str]
    use_auto_process: bool


def parse_custom_words(raw: str) -> List[str]:
    if not raw:
        return []
    separators = [",", "\n", ";"]
    tokens = [raw]
    for sep in separators:
        tokens = sum([token.split(sep) for token in tokens], [])
    return [token.strip() for token in tokens if token.strip()]


def run_processing(text: str, config: ShieldConfig, tone_label: str) -> tuple[ShieldResult, RewriteResult]:
    tone = next((tone for tone in AVAILABLE_TONES if tone.name == tone_label), AVAILABLE_TONES[0])
    shield_result = shield_text(text, config)
    rewrite_result = rewrite_text(shield_result.sanitized_text, tone)
    return shield_result, rewrite_result


def display_results(original: str, shield_result: ShieldResult, rewrite_result: RewriteResult) -> None:
    st.subheader("Protection summary")
    metrics = st.columns(3)
    metrics[0].metric("Shielded words", shield_result.total_matches)
    metrics[1].metric("Active tone", rewrite_result.tone.name)
    metrics[2].metric("Categories flagged", sum(1 for count in shield_result.matches_by_category.values() if count))

    col_original, col_shielded = st.columns(2)
    with col_original:
        st.markdown("#### Original message")
        st.write(original if original.strip() else "_No text provided yet._")
    with col_shielded:
        st.markdown("#### Shielded message")
        st.write(shield_result.sanitized_text if original.strip() else "_Awaiting input._")

    st.markdown("#### Rewritten tone")
    st.info(rewrite_result.rewritten_text)

    with st.expander("View shield activity", expanded=False):
        if shield_result.total_matches == 0:
            st.write("No shielded language detected.")
        else:
            st.write("Word counts by category:")
            table_rows = [
                {
                    "Category": category,
                    "Matches": shield_result.matches_by_category.get(category, 0),
                }
                for category in shield_result.matches_by_category.keys()
            ]
            st.table(table_rows)
            st.write("Flagged words:")
            st.write(
                ", ".join(
                    f"{match.word} → {match.replacement} ({match.category})"
                    for match in shield_result.matched_words
                )
            )

    st.caption(rewrite_result.guidance)


def layout_sidebar(base_config: ShieldConfig) -> AppState:
    st.sidebar.header("Shield settings")
    tone_label = st.sidebar.radio(
        "Rewrite tone",
        options=[tone.name for tone in AVAILABLE_TONES],
        format_func=lambda value: value,
    )

    categories = list(base_config.categories.keys())
    active_categories = st.sidebar.multiselect(
        "Active shield categories",
        options=categories,
        default=categories,
        help="Choose which categories of protective language should be active.",
    )

    extra_words = parse_custom_words(
        st.sidebar.text_area(
            "Custom words to shield",
            placeholder="Add extra words separated by commas or new lines",
        )
    )

    use_auto_process = st.sidebar.toggle(
        "Process automatically",
        value=True,
        help="When enabled, the message is processed immediately as you type.",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "Need GPT-powered rewrites? Connect this UI to your FastAPI backend via the options"
        " in `text_angel_briefing.txt`."
    )

    return AppState(
        tone_label=tone_label,
        extra_words=extra_words,
        active_categories=active_categories,
        use_auto_process=use_auto_process,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🪽", layout="centered")
    st.title(APP_TITLE)
    st.write(
        "Text Angel shields sensitive language and offers tone rewrites so conversations"
        " stay kind, professional, and emotionally safe."
    )

    try:
        base_config = load_config(SHIELD_PATH)
    except ShieldingError as error:
        st.error(f"Unable to load shield configuration: {error}")
        st.stop()

    state = layout_sidebar(base_config)

    with st.form("text-angel-form", clear_on_submit=False):
        message = st.text_area(
            "Write or paste the message you'd like Text Angel to protect",
            placeholder="Type something that needs a little more care...",
            height=200,
        )
        submit = st.form_submit_button("Shield & Rewrite")

    active_config = build_active_config(base_config, state.active_categories, state.extra_words)

    should_process = state.use_auto_process or submit
    if should_process and message:
        shield_result, rewrite_result = run_processing(message, active_config, state.tone_label)
        display_results(message, shield_result, rewrite_result)
    else:
        st.info("Add a message to begin shielding and rewriting.")


if __name__ == "__main__":
    main()

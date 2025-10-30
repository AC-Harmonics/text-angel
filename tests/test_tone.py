"""Tests for tone rewriting helpers."""

from text_angel import AVAILABLE_TONES, rewrite_text


def test_rewrite_returns_text_with_prefix() -> None:
    tone = AVAILABLE_TONES[0]
    result = rewrite_text("I hate this", tone)
    assert result.rewritten_text.startswith("I want to share this gently")


def test_rewrite_softens_language() -> None:
    tone = next(t for t in AVAILABLE_TONES if t.name == "Gentle & Kind")
    result = rewrite_text("I hate this", tone)
    assert "really dislike" in result.rewritten_text

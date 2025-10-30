"""Tone rewriting helpers for the Text Angel Streamlit experience."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

import re


@dataclass(frozen=True)
class ToneProfile:
    """Represents a tone option exposed in the UI."""

    name: str
    description: str
    transform: Callable[[str], str]


@dataclass(frozen=True)
class RewriteResult:
    """Result of rewriting a user message."""

    tone: ToneProfile
    rewritten_text: str
    guidance: str


SOFTEN_REPLACEMENTS = {
    r"\bcan't\b": "may not be able to",
    r"\bwon't\b": "might not",
    r"\bshouldn't\b": "may want to avoid",
    r"\bhate\b": "really dislike",
    r"\bidiot\b": "person",
    r"\bshut up\b": "let's pause",
    r"\bdumb\b": "not helpful",
    r"\bkill\b": "stop",
    r"\bstupid\b": "unhelpful",
}

POLITE_REPLACEMENTS = {
    r"\bhey\b": "hello",
    r"\bhi\b": "hello",
    r"\bthanks\b": "thank you",
    r"\bplease\b": "please",
    r"\bsorry\b": "I apologize",
}


def _apply_replacements(text: str, replacements: Dict[str, str]) -> str:
    result = text
    for pattern, repl in replacements.items():
        result = re.sub(pattern, repl, result, flags=re.IGNORECASE)
    return result


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _sentence_case(text: str) -> str:
    if not text:
        return text
    text = text.strip()
    return text[0].upper() + text[1:]


def _ensure_period(text: str) -> str:
    if not text:
        return text
    if text[-1] in {".", "!", "?"}:
        return text
    return text + "."


def _gentle_transform(text: str) -> str:
    softened = _apply_replacements(text, SOFTEN_REPLACEMENTS)
    softened = _normalize_whitespace(softened)
    softened = _sentence_case(softened)
    softened = _ensure_period(softened)
    return f"I want to share this gently: {softened}"


def _professional_transform(text: str) -> str:
    polished = _apply_replacements(text, {**SOFTEN_REPLACEMENTS, **POLITE_REPLACEMENTS})
    polished = _normalize_whitespace(polished)
    polished = _sentence_case(polished)
    polished = _ensure_period(polished)
    return f"For clarity, {polished} I appreciate your attention to this matter."


def _empathetic_transform(text: str) -> str:
    softened = _apply_replacements(text, SOFTEN_REPLACEMENTS)
    softened = _normalize_whitespace(softened)
    softened = _sentence_case(softened)
    softened = _ensure_period(softened)
    return (
        "I hear how important this is and I want to respond with care: "
        f"{softened} I'm here with you and open to continuing the conversation."
    )


def _direct_transform(text: str) -> str:
    normalized = _normalize_whitespace(text)
    normalized = _sentence_case(normalized)
    normalized = _ensure_period(normalized)
    return f"Here's the message in a clear, calm tone: {normalized}"


AVAILABLE_TONES: List[ToneProfile] = [
    ToneProfile(
        name="Gentle & Kind",
        description="Softens the language and adds a gentle introduction.",
        transform=_gentle_transform,
    ),
    ToneProfile(
        name="Professional",
        description="Adds polish suitable for workplace conversations.",
        transform=_professional_transform,
    ),
    ToneProfile(
        name="Empathetic",
        description="Centers care and emotional validation.",
        transform=_empathetic_transform,
    ),
    ToneProfile(
        name="Calm & Direct",
        description="Keeps the core message while removing sharp edges.",
        transform=_direct_transform,
    ),
]


def rewrite_text(text: str, tone: ToneProfile) -> RewriteResult:
    """Rewrite ``text`` according to the provided ``tone`` profile."""

    rewritten = tone.transform(text)
    guidance = (
        "This rewrite uses Text Angel's local tone templates. "
        "For production deployments you can connect the app to the hosted API "
        "for GPT-powered rewrites."
    )
    return RewriteResult(tone=tone, rewritten_text=rewritten, guidance=guidance)

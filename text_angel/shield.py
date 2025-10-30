"""Shield word filtering utilities for the Text Angel project."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping


@dataclass(frozen=True)
class ShieldMatch:
    """Represents a single category match in the shield filter."""

    category: str
    word: str
    replacement: str


@dataclass(frozen=True)
class ShieldResult:
    """Container returned after shielding text."""

    sanitized_text: str
    total_matches: int
    matches_by_category: Mapping[str, int]
    matched_words: List[ShieldMatch]


@dataclass(frozen=True)
class ShieldConfig:
    """Configuration for the shield filter."""

    categories: Mapping[str, List[str]]
    replacement: str = "🛡️"

    def compile_patterns(self) -> Mapping[str, re.Pattern[str]]:
        """Precompile regex patterns for every category.

        Returns
        -------
        Mapping[str, Pattern]
            A dictionary mapping category names to compiled regular
            expressions that match any word in the category.
        """

        compiled: Dict[str, re.Pattern[str]] = {}
        for category, words in self.categories.items():
            if not words:
                continue
            escaped = (re.escape(word.strip()) for word in words if word.strip())
            joined = "|".join(word for word in escaped if word)
            if not joined:
                continue
            compiled[category] = re.compile(rf"\b({joined})\b", re.IGNORECASE)
        return compiled


class ShieldingError(RuntimeError):
    """Raised when the shield configuration cannot be loaded."""


def _validate_config(raw: Mapping[str, Iterable[str]]) -> Dict[str, List[str]]:
    validated: Dict[str, List[str]] = {}
    for key, words in raw.items():
        if not isinstance(key, str):
            raise ShieldingError("Shield category keys must be strings.")
        if not isinstance(words, Iterable):
            raise ShieldingError("Shield category values must be iterable.")
        cleaned = []
        for word in words:
            if not isinstance(word, str):
                raise ShieldingError(
                    f"Invalid word for category '{key}'. Only strings are allowed."
                )
            word = word.strip()
            if word:
                cleaned.append(word)
        validated[key] = cleaned
    if not validated:
        raise ShieldingError("Shield configuration must define at least one category.")
    return validated


def load_shield_config(path: Path) -> ShieldConfig:
    """Load the shield configuration from a JSON file."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ShieldingError(f"Shield configuration not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ShieldingError(f"Shield configuration is not valid JSON: {path}") from exc

    if not isinstance(data, Mapping):
        raise ShieldingError("Shield configuration must be an object mapping categories to words.")

    categories = _validate_config(data)
    return ShieldConfig(categories=categories)


def shield_text(text: str, config: ShieldConfig) -> ShieldResult:
    """Apply the shield filter to the provided text."""

    patterns = config.compile_patterns()
    matches_by_category: MutableMapping[str, int] = {
        key: 0 for key in config.categories.keys()
    }
    matched_words: List[ShieldMatch] = []
    sanitized_text = text

    for category, pattern in patterns.items():
        def replacement(match: re.Match[str]) -> str:
            word = match.group(0)
            matches_by_category[category] += 1
            matched_words.append(
                ShieldMatch(category=category, word=word, replacement=config.replacement)
            )
            return config.replacement

        sanitized_text = pattern.sub(replacement, sanitized_text)

    total_matches = sum(matches_by_category.values())

    return ShieldResult(
        sanitized_text=sanitized_text,
        total_matches=total_matches,
        matches_by_category=dict(matches_by_category),
        matched_words=matched_words,
    )

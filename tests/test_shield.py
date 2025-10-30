from pathlib import Path

import pytest

from text_angel import ShieldConfig, load_shield_config, shield_text


@pytest.fixture()
def shield_config(tmp_path: Path) -> ShieldConfig:
    config_path = tmp_path / "shield.json"
    config_path.write_text('{"kindness": ["mean", "dumb"], "anger": ["hate"]}', encoding="utf-8")
    return load_shield_config(config_path)


def test_shield_replaces_words(shield_config: ShieldConfig) -> None:
    result = shield_text("This is mean and dumb", shield_config)
    assert result.sanitized_text.count("🛡️") == 2
    assert result.total_matches == 2
    assert result.matches_by_category["kindness"] == 2


def test_shield_handles_multiple_categories(shield_config: ShieldConfig) -> None:
    result = shield_text("I hate being mean", shield_config)
    assert result.total_matches == 2
    assert result.matches_by_category["anger"] == 1
    assert result.matches_by_category["kindness"] == 1

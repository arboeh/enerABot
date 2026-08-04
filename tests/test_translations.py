# tests/test_translations.py

"""Test that translation files have consistent keys across languages."""

import json
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "enerabot" / "translations"
STRINGS_PATH = TRANSLATIONS_DIR.parent / "strings.json"


def _flatten_keys(data: dict, prefix: str = "") -> set[str]:
    keys = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys |= _flatten_keys(value, full_key)
        else:
            keys.add(full_key)
    return keys


def test_de_and_en_have_same_keys() -> None:
    """German and English translations must expose identical key structures."""
    de = json.loads((TRANSLATIONS_DIR / "de.json").read_text(encoding="utf-8"))
    en = json.loads((TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"))
    assert _flatten_keys(de) == _flatten_keys(en)


def test_strings_json_has_no_hassfest_forbidden_keys() -> None:
    """services fields in strings.json must not contain selector/required/example."""
    data = json.loads(STRINGS_PATH.read_text(encoding="utf-8"))
    services = data.get("services", {})
    forbidden = {"selector", "required", "example"}
    for service in services.values():
        for field in service.get("fields", {}).values():
            assert forbidden.isdisjoint(field.keys())

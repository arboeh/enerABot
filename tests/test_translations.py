# tests/test_translations.py

"""Test that translation files have consistent keys across languages."""

import json
import re
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


def test_number_and_select_keys_present() -> None:
    """Test that number and select entity translations exist."""
    en = json.loads((TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"))
    assert "number" in en["entity"]
    assert "tariff_price" in en["entity"]["number"]
    assert "offset" in en["entity"]["number"]
    assert "select" in en["entity"]
    assert "price_mode" in en["entity"]["select"]
    assert "cost_reset_cycle" in en["entity"]["select"]


def test_config_step_user_has_price_sensor_key() -> None:
    """The config flow user step must translate price_sensor in all files."""
    de = json.loads((TRANSLATIONS_DIR / "de.json").read_text(encoding="utf-8"))
    en = json.loads((TRANSLATIONS_DIR / "en.json").read_text(encoding="utf-8"))
    strings = json.loads(STRINGS_PATH.read_text(encoding="utf-8"))

    for name, data in (("strings.json", strings), ("en.json", en), ("de.json", de)):
        assert "price_sensor" in data["config"]["step"]["user"]["data"], (
            f"price_sensor missing in {name} config.step.user.data"
        )


def test_config_flow_schema_keys_have_translations() -> None:
    """Every field in STEP_USER_DATA_SCHEMA must have a strings.json label."""
    from custom_components.enerabot.config_flow import STEP_USER_DATA_SCHEMA

    strings = json.loads(STRINGS_PATH.read_text(encoding="utf-8"))
    translated_keys = set(strings["config"]["step"]["user"]["data"].keys())
    schema_keys = {str(key.schema) if hasattr(key, "schema") else str(key) for key in STEP_USER_DATA_SCHEMA.schema}
    missing = schema_keys - translated_keys
    assert not missing, f"Missing translations for config flow fields: {missing}"


USER_DATA_FIELDS = [
    "name", "sensor", "obis_code", "initial_meter_value", "meter_id",
    "tariff_price", "price_mode", "price_sensor", "cost_reset_cycle", "reading_cycle",
]

INIT_DATA_FIELDS = [
    "meter_value", "meter_id", "obis_code", "tariff_price",
    "price_mode", "price_sensor", "cost_reset_cycle",
]

_SUFFIX_RE = re.compile(r"\((Pflicht|Optional|Required)")
_UNIT_RE = re.compile(r"\b(kWh|EUR/kWh|EUR)\b")


def _extract_field_text(data: dict, fields: list[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for field in fields:
        entry = data.get(field)
        if isinstance(entry, dict):
            texts[field] = entry.get("description", "") or entry.get("name", "")
        else:
            texts[field] = entry or ""
    return texts


def test_field_descriptions_have_requirement_suffixes() -> None:
    """Every field label/description must end with a requirement suffix."""
    for filename in ("de.json", "en.json"):
        data = json.loads((TRANSLATIONS_DIR / filename).read_text(encoding="utf-8"))
        for step_key, fields in (
            ("user", USER_DATA_FIELDS),
            ("init", INIT_DATA_FIELDS),
        ):
            step_data = (
                data["config"]["step"][step_key]["data"]
                if step_key == "user"
                else data["options"]["step"][step_key]["data"]
            )
            texts = _extract_field_text(step_data, fields)
            for field, text in texts.items():
                assert _SUFFIX_RE.search(text), (
                    f"{filename}: field '{field}' in step.{step_key}.data "
                    f"missing requirement suffix: '{text}'"
                )


def test_field_descriptions_have_no_unit_text() -> None:
    """Field labels/descriptions must not contain hardcoded unit text."""
    for filename in ("de.json", "en.json"):
        data = json.loads((TRANSLATIONS_DIR / filename).read_text(encoding="utf-8"))
        for step_key, fields in (
            ("user", USER_DATA_FIELDS),
            ("init", INIT_DATA_FIELDS),
        ):
            step_data = (
                data["config"]["step"][step_key]["data"]
                if step_key == "user"
                else data["options"]["step"][step_key]["data"]
            )
            texts = _extract_field_text(step_data, fields)
            for field, text in texts.items():
                assert not _UNIT_RE.search(text), (
                    f"{filename}: field '{field}' in step.{step_key}.data "
                    f"contains forbidden unit text: '{text}'"
                )

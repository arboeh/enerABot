# tests/test_services.py

"""Test that services.yaml is valid YAML and parses without errors."""

from pathlib import Path

import yaml

SERVICES_PATH = Path(__file__).parent.parent / "custom_components" / "enerabot" / "services.yaml"


def test_services_yaml_parses() -> None:
    """services.yaml must be valid YAML with no parsing errors."""
    with open(SERVICES_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert isinstance(data, dict)
    assert "set_energy_meter" in data
    assert "reset_meter" in data
    for service in data.values():
        assert "name" in service
        assert "fields" in service

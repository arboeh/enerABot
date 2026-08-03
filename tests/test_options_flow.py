# tests/test_options_flow.py

"""Tests for the enerABot options flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import DOMAIN

MOCK_CONFIG = {
    "name": "Test Meter",
    "import_sensor": "sensor.test_import",
    "export_sensor": "sensor.test_export",
}


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {"import_value": 100.0, "export_value": 50.0}
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
async def setup_entry(hass, mock_coordinator):
    """Set up a config entry with mocked coordinator."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test_entry")
    entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["test_entry"] = mock_coordinator
    return entry


async def test_options_flow_init_shows_menu(hass, setup_entry):
    """Init step should show the main menu."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)

    assert result["type"] == "menu"
    assert result["step_id"] == "init"
    assert "import" in result["menu_options"]
    assert "export" in result["menu_options"]


async def test_options_flow_import_shows_form(hass, setup_entry):
    """Import step should show a form when no input given."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"next_step_id": "import"})

    assert result["type"] == "form"
    assert result["step_id"] == "import"
    assert result["errors"] == {}


async def test_options_flow_import_success(hass, setup_entry):
    """Import correction should complete when sensor is available."""
    with patch(
        "homeassistant.core.HomeAssistant.states",
    ):
        result = await hass.config_entries.options.async_init(setup_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={"next_step_id": "import"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"meter_value": 1000.0},
        )

    assert result["type"] == "create_entry"


async def test_options_flow_export_shows_form(hass, setup_entry):
    """Export step should show a form when no input given."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"next_step_id": "export"})

    assert result["type"] == "form"
    assert result["step_id"] == "export"
    assert result["errors"] == {}

# tests/test_options_flow.py

"""Tests for the enerABot options flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    CONF_METER_ID_IMPORT,
    CONF_OBIS_CODE_IMPORT,
    CONF_TARIFF_PRICE_IMPORT,
    DOMAIN,
)

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


@pytest.fixture
async def setup_entry_import_only(hass, mock_coordinator):
    """Set up a config entry with only an import sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Test Import Only",
            CONF_IMPORT_SENSOR: "sensor.test_import",
        },
        entry_id="test_entry_import_only",
    )
    entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["test_entry_import_only"] = mock_coordinator
    return entry


@pytest.fixture
async def setup_entry_export_only(hass, mock_coordinator):
    """Set up a config entry with only an export sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Test Export Only",
            CONF_EXPORT_SENSOR: "sensor.test_export",
        },
        entry_id="test_entry_export_only",
    )
    entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["test_entry_export_only"] = mock_coordinator
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
    hass.states.async_set("sensor.test_import", "1000.0")
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"next_step_id": "import"})
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


async def test_options_flow_menu_import_only(hass, setup_entry_import_only):
    """Menu should show only import option when only import sensor is configured."""
    result = await hass.config_entries.options.async_init(setup_entry_import_only.entry_id)

    assert result["type"] == "menu"
    assert result["step_id"] == "init"
    assert "import" in result["menu_options"]
    assert "export" not in result["menu_options"]


async def test_options_flow_menu_export_only(hass, setup_entry_export_only):
    """Menu should show only export option when only export sensor is configured."""
    result = await hass.config_entries.options.async_init(setup_entry_export_only.entry_id)

    assert result["type"] == "menu"
    assert result["step_id"] == "init"
    assert "export" in result["menu_options"]
    assert "import" not in result["menu_options"]


async def test_options_flow_import_updates_metadata(hass, setup_entry):
    """Import correction should also update OBIS code and meter ID."""
    hass.states.async_set("sensor.test_import", "1000.0")
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"next_step_id": "import"})
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "meter_value": 1000.0,
            "meter_id_import": "1SAG9999999999",
            "obis_code_import": "1.8.2",
            "tariff_price_import": 0.35,
        },
    )
    assert result["type"] == "create_entry"
    assert setup_entry.options.get(CONF_METER_ID_IMPORT) == "1SAG9999999999"
    assert setup_entry.options.get(CONF_OBIS_CODE_IMPORT) == "1.8.2"
    assert setup_entry.options.get(CONF_TARIFF_PRICE_IMPORT) == 0.35

# tests/test_options_flow.py

"""Tests for the enerABot options flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_METER_ID,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    DOMAIN,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
)


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {"value": 100.0}
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
async def setup_entry(hass, mock_coordinator):
    """Set up a config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.0,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
        },
        entry_id="test_entry",
    )
    entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["test_entry"] = mock_coordinator
    return entry


@pytest.fixture
async def setup_entry_no_sensor(hass, mock_coordinator):
    """Set up a config entry without a sensor entity in data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.0,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
        },
        entry_id="test_entry_no_sensor",
    )
    entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["test_entry_no_sensor"] = mock_coordinator
    return entry


async def test_options_flow_init_shows_form(hass, setup_entry):
    """Init step should show a form."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)

    assert result["type"] == "form"
    assert result["step_id"] == "init"


async def test_options_flow_correction_success(hass, setup_entry):
    """Correction should complete when sensor is available."""
    hass.states.async_set("sensor.test_import", "1000.0")
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"meter_value": 1000.0},
    )

    assert result["type"] == "create_entry"


async def test_options_flow_updates_metadata(hass, setup_entry):
    """Correction should also update OBIS code and meter ID."""
    hass.states.async_set("sensor.test_import", "1000.0")
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "meter_value": 1000.0,
            "meter_id": "1SAG9999999999",
            "obis_code": "1.8.2",
            "tariff_price": 0.35,
        },
    )
    assert result["type"] == "create_entry"
    assert setup_entry.options.get(CONF_METER_ID) == "1SAG9999999999"
    assert setup_entry.options.get(CONF_OBIS_CODE) == "1.8.2"
    assert setup_entry.options.get(CONF_TARIFF_PRICE) == 0.35

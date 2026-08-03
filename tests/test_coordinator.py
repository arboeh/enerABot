# tests/test_coordinator.py

"""Test the enerABot coordinator."""

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    CONF_NAME,
    DOMAIN,
)
from custom_components.enerabot.coordinator import EnerABotCoordinator


@pytest.fixture
def mock_config_entry(hass):
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter Pair",
        data={
            CONF_NAME: "Test Meter",
            CONF_IMPORT_SENSOR: "sensor.test_import",
            CONF_EXPORT_SENSOR: "sensor.test_export",
        },
        options={
            "offset_import": 1.5,
            "offset_export": 0.5,
        },
        unique_id="sensor.test_import_sensor.test_export",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_config_entry_export_only(hass):
    """Create a mock config entry with only an export sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Export Only",
        data={
            CONF_NAME: "Test Export Only",
            CONF_EXPORT_SENSOR: "sensor.test_export",
        },
        options={
            "offset_export": 0.5,
        },
        unique_id="none_sensor.test_export",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_config_entry_import_only(hass):
    """Create a mock config entry with only an import sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Import Only",
        data={
            CONF_NAME: "Test Import Only",
            CONF_IMPORT_SENSOR: "sensor.test_import",
        },
        options={
            "offset_import": 1.5,
        },
        unique_id="sensor.test_import_none",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_coordinator(hass, mock_config_entry):
    """Create a coordinator."""
    coordinator = EnerABotCoordinator(hass, mock_config_entry)
    return coordinator


@pytest.fixture
def mock_coordinator_export_only(hass, mock_config_entry_export_only):
    """Create a coordinator with only an export sensor."""
    coordinator = EnerABotCoordinator(hass, mock_config_entry_export_only)
    return coordinator


async def test_coordinator_update_data(hass: HomeAssistant, mock_coordinator):
    """Test coordinator data update with offsets applied."""
    hass.states.async_set("sensor.test_import", "100.0")
    hass.states.async_set("sensor.test_export", "100.0")

    data = await mock_coordinator._async_update_data()

    assert data["import_value"] == 101.5
    assert data["export_value"] == 100.5


async def test_coordinator_update_data_no_offset(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test coordinator data update without offsets."""
    hass.config_entries.async_update_entry(mock_config_entry, options={})
    await hass.async_block_till_done()

    hass.states.async_set("sensor.test_import", "100.0")
    hass.states.async_set("sensor.test_export", "100.0")

    data = await mock_coordinator._async_update_data()

    assert data["import_value"] == 100.0
    assert data["export_value"] == 100.0


async def test_coordinator_update_data_unavailable(hass: HomeAssistant, mock_coordinator):
    """Test coordinator handles unavailable sensor gracefully."""
    hass.states.async_set("sensor.test_import", "unavailable")
    hass.states.async_set("sensor.test_export", "unavailable")

    data = await mock_coordinator._async_update_data()

    assert data["import_value"] is None
    assert data["export_value"] is None


async def test_coordinator_update_data_unknown(hass: HomeAssistant, mock_coordinator):
    """Test coordinator handles unknown sensor gracefully."""
    hass.states.async_set("sensor.test_import", "unknown")
    hass.states.async_set("sensor.test_export", "unknown")

    data = await mock_coordinator._async_update_data()

    assert data["import_value"] is None
    assert data["export_value"] is None


async def test_coordinator_export_only(hass: HomeAssistant, mock_coordinator_export_only):
    """Test coordinator with only export sensor configured."""
    hass.states.async_set("sensor.test_export", "100.0")

    data = await mock_coordinator_export_only._async_update_data()

    assert data["import_value"] is None
    assert data["export_value"] == 100.5

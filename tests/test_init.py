# tests/test_init.py

"""Tests for the enerABot __init__ module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot import (
    _calculate_and_store_offset,
    _register_services,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.enerabot.const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    CONF_NAME,
    DOMAIN,
    OPTION_OFFSET_EXPORT,
    OPTION_OFFSET_IMPORT,
)


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
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
            OPTION_OFFSET_IMPORT: 0.0,
            OPTION_OFFSET_EXPORT: 0.0,
        },
        unique_id="sensor.test_import_sensor.test_export",
    )
    entry.add_to_hass(hass)
    return entry


async def test_register_services_import(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that the import service registers and sets the offset."""
    mock_config_entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})

    with patch(
        "custom_components.enerabot._calculate_and_store_offset",
        new_callable=AsyncMock,
    ) as mock_calc:
        await hass.services.async_call(
            DOMAIN,
            "set_energy_meter_import",
            {
                "entity_id": "sensor.test_import",
                "meter_value": 1234.5,
            },
            blocking=True,
        )
        mock_calc.assert_called_once()
        call_args = mock_calc.call_args
        assert call_args[1]["entity_id"] == "sensor.test_import"
        assert call_args[1]["meter_value"] == 1234.5
        assert call_args[1]["is_import"] is True


async def test_register_services_export(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that the export service registers and sets the offset."""
    mock_config_entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})

    with patch(
        "custom_components.enerabot._calculate_and_store_offset",
        new_callable=AsyncMock,
    ) as mock_calc:
        await hass.services.async_call(
            DOMAIN,
            "set_energy_meter_export",
            {
                "entity_id": "sensor.test_export",
                "meter_value": 567.8,
            },
            blocking=True,
        )
        mock_calc.assert_called_once()
        call_args = mock_calc.call_args
        assert call_args[1]["entity_id"] == "sensor.test_export"
        assert call_args[1]["meter_value"] == 567.8
        assert call_args[1]["is_import"] is False


async def test_calculate_and_store_offset_no_matching_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that a warning is logged when no matching config entry is found."""
    mock_config_entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})

    with patch("custom_components.enerabot._LOGGER.warning") as mock_warning:
        await _calculate_and_store_offset(hass, "sensor.nonexistent", 1000.0, is_import=True)
        mock_warning.assert_called_once_with("No matching config entry found for entity %s", "sensor.nonexistent")


async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that async_unload_entry removes the coordinator and deregisters services."""
    mock_config_entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})

    with patch(
        "custom_components.enerabot.EnerABotCoordinator.async_config_entry_first_refresh",
        new=AsyncMock(),
    ):
        await async_setup_entry(hass, mock_config_entry)

    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    result = await async_unload_entry(hass, mock_config_entry)

    assert result is True
    assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})


async def test_async_reload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that async_reload_entry unloads and sets up the entry again."""
    mock_config_entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})

    with patch(
        "custom_components.enerabot.EnerABotCoordinator.async_config_entry_first_refresh",
        new=AsyncMock(),
    ):
        await async_setup_entry(hass, mock_config_entry)

    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    with (
        patch.object(hass.config_entries, "async_unload", new=AsyncMock(return_value=True)),
        patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()),
        patch(
            "custom_components.enerabot.EnerABotCoordinator.async_config_entry_first_refresh",
            new=AsyncMock(),
        ),
    ):
        await async_reload_entry(hass, mock_config_entry)

    assert mock_config_entry.entry_id in hass.data[DOMAIN]

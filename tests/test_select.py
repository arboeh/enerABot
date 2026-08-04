"""Tests for the enerABot select platform."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_COST_RESET_CYCLE,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_PRICE_MODE,
    CONF_SENSOR,
    COST_RESET_MONTHLY,
    COST_RESET_NONE,
    DOMAIN,
    PRICE_MODE_DYNAMIC,
    PRICE_MODE_FIXED,
    PRICE_MODE_NONE,
)
from custom_components.enerabot.select import (
    EnerABotCostResetCycleSelect,
    EnerABotPriceModeSelect,
)


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry with price mode and cost reset cycle."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter",
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_COST_RESET_CYCLE: COST_RESET_MONTHLY,
        },
        unique_id="sensor.test_import_select",
    )
    entry.add_to_hass(hass)
    return entry


async def test_price_mode_select_current_option(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that current_option returns the configured price mode."""
    entity = EnerABotPriceModeSelect(hass, mock_config_entry)
    assert entity.current_option == PRICE_MODE_FIXED


async def test_price_mode_select_defaults_to_none(hass: HomeAssistant) -> None:
    """Test that current_option defaults to none when unset."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="No Mode",
        data={
            CONF_NAME: "No Mode",
            CONF_SENSOR: "sensor.test_no_mode",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={},
        unique_id="sensor.test_no_mode",
    )
    entry.add_to_hass(hass)
    entity = EnerABotPriceModeSelect(hass, entry)
    assert entity.current_option == PRICE_MODE_NONE


async def test_price_mode_select_option_updates_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that selecting an option updates the config entry."""
    entity = EnerABotPriceModeSelect(hass, mock_config_entry)
    await entity.async_select_option(PRICE_MODE_DYNAMIC)
    await hass.async_block_till_done()
    assert mock_config_entry.options[CONF_PRICE_MODE] == PRICE_MODE_DYNAMIC


async def test_price_mode_select_is_config_category(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that the entity is grouped as a configuration entity."""
    entity = EnerABotPriceModeSelect(hass, mock_config_entry)
    assert entity.entity_category == "config"


async def test_cost_reset_cycle_select_current_option(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that current_option returns the configured reset cycle."""
    entity = EnerABotCostResetCycleSelect(hass, mock_config_entry)
    assert entity.current_option == COST_RESET_MONTHLY


async def test_cost_reset_cycle_select_option_updates_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test that selecting an option updates the config entry."""
    entity = EnerABotCostResetCycleSelect(hass, mock_config_entry)
    await entity.async_select_option(COST_RESET_NONE)
    await hass.async_block_till_done()
    assert mock_config_entry.options[CONF_COST_RESET_CYCLE] == COST_RESET_NONE

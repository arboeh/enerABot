"""Tests for the enerABot number platform."""

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    DOMAIN,
    OPTION_OFFSET,
)
from custom_components.enerabot.number import (
    EnerABotOffsetNumber,
    EnerABotTariffPriceNumber,
)


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry with tariff price and offset."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter",
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            CONF_TARIFF_PRICE: 0.30,
            OPTION_OFFSET: 1.5,
        },
        unique_id="sensor.test_import_number",
    )
    entry.add_to_hass(hass)
    return entry


async def test_tariff_price_number_native_value(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that native_value returns the configured tariff price."""
    entity = EnerABotTariffPriceNumber(hass, mock_config_entry)
    assert entity.native_value == 0.30


async def test_tariff_price_number_native_value_none(
    hass: HomeAssistant,
) -> None:
    """Test that native_value returns None when tariff price is unset."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="No Price",
        data={
            CONF_NAME: "No Price",
            CONF_SENSOR: "sensor.test_no_price",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={},
        unique_id="sensor.test_no_price",
    )
    entry.add_to_hass(hass)
    entity = EnerABotTariffPriceNumber(hass, entry)
    assert entity.native_value is None


async def test_tariff_price_number_set_value_updates_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test that setting the value updates the config entry options."""
    entity = EnerABotTariffPriceNumber(hass, mock_config_entry)
    await entity.async_set_native_value(0.45)
    await hass.async_block_till_done()
    assert mock_config_entry.options[CONF_TARIFF_PRICE] == 0.45


async def test_tariff_price_number_is_config_category(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that the entity is grouped as a configuration entity."""
    entity = EnerABotTariffPriceNumber(hass, mock_config_entry)
    assert entity.entity_category == "config"


async def test_offset_number_native_value(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that native_value returns the configured offset."""
    entity = EnerABotOffsetNumber(hass, mock_config_entry)
    assert entity.native_value == 1.5


async def test_offset_number_set_value_updates_entry(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that setting the offset updates the config entry options."""
    entity = EnerABotOffsetNumber(hass, mock_config_entry)
    await entity.async_set_native_value(2.75)
    await hass.async_block_till_done()
    assert mock_config_entry.options[OPTION_OFFSET] == 2.75


async def test_offset_number_disabled_by_default(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that the offset entity is disabled by default."""
    entity = EnerABotOffsetNumber(hass, mock_config_entry)
    assert entity.entity_registry_enabled_default is False


async def test_number_platform_setup(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test that both number entities are created via async_setup_entry."""
    from unittest.mock import AsyncMock, patch

    with (
        patch(
            "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
            return_value=100.5,
        ),
        patch(
            "custom_components.enerabot.coordinator.EnerABotCoordinator.async_config_entry_first_refresh",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.enerabot.coordinator.EnerABotCoordinator.async_start_state_listener",
            new=AsyncMock(),
        ),
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert hass.states.async_entity_ids("number") != []

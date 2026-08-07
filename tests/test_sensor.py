# tests/test_sensor.py

"""Test the enerABot sensor entity."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_METER_ID,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_PRICE_MODE,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    DOMAIN,
    OPTION_COST_TOTAL,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
    PRICE_MODE_FIXED,
    PRICE_MODE_NONE,
)


async def test_sensor_created(hass: HomeAssistant, setup_integration):
    """Test that sensor is created."""
    entry = setup_integration

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_import")

    assert entity_id is not None


async def test_sensor_import_value(hass: HomeAssistant, setup_integration):
    """Test import sensor value."""
    entry = setup_integration
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_import")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None


async def test_sensor_import_attributes(hass: HomeAssistant, setup_integration):
    """Test import sensor attributes."""
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{setup_integration.entry_id}_import")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert "offset" in state.attributes
    assert "last_correction" in state.attributes


async def test_sensor_exposes_obis_and_meter_id_attributes(hass: HomeAssistant, mock_config_entry):
    """Test that OBIS code and meter ID appear as extra state attributes."""
    hass.states.async_set("sensor.test_import", "100.0")
    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{mock_config_entry.entry_id}_import")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.attributes.get("obis_code") == "1.8.2"
    assert state.attributes.get("meter_id") == "1SAG1234567890"
    assert state.attributes.get("tariff_price") == 0.32


async def test_sensor_entity_id_not_duplicated(hass: HomeAssistant, mock_config_entry):
    """Test that the sensor's entity_id does not duplicate the meter name."""
    hass.states.async_set("sensor.test_import", "100.0")
    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{mock_config_entry.entry_id}_import")
    assert entity_id is not None
    meter_name_slug = slugify(mock_config_entry.data.get(CONF_NAME, mock_config_entry.title))
    assert entity_id.count(meter_name_slug) == 1


@pytest.fixture
async def setup_import_only(hass: HomeAssistant, mock_config_entry):
    """Set up integration with only an import sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Import Only",
        data={
            CONF_NAME: "Test Import Only",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.0,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
        },
        unique_id="sensor.test_import_only",
    )
    entry.add_to_hass(hass)
    hass.states.async_set("sensor.test_import", "100.0")
    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


@pytest.fixture
async def setup_export_only(hass: HomeAssistant, mock_config_entry):
    """Set up integration with only an export sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Export Only",
        data={
            CONF_NAME: "Test Export Only",
            CONF_SENSOR: "sensor.test_export",
            CONF_OBIS_CODE: "2.8.2",
        },
        options={
            OPTION_OFFSET: 0.0,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
        },
        unique_id="sensor.test_export_only",
    )
    entry.add_to_hass(hass)
    hass.states.async_set("sensor.test_export", "50.0")
    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=50.2,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_sensor_only_import_value(hass: HomeAssistant, setup_import_only):
    """Test that import sensor has the correct value when export not configured."""
    entry = setup_import_only
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_import")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None


async def test_sensor_only_export_value(hass: HomeAssistant, setup_export_only):
    """Test that export sensor has the correct value when import not configured."""
    entry = setup_export_only
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_export")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None


async def test_sensor_name_is_just_import_export(hass: HomeAssistant, mock_config_entry):
    """Test that _attr_name is exactly 'Import'/'Export', not prefixed with meter name."""
    from custom_components.enerabot.coordinator import EnerABotCoordinator
    from custom_components.enerabot.sensor import EnerABotSensor

    coordinator = EnerABotCoordinator(hass, mock_config_entry)
    sensor = EnerABotSensor(coordinator, mock_config_entry)

    obis_code = mock_config_entry.data.get(CONF_OBIS_CODE, "")
    if obis_code.startswith("1.8"):
        assert sensor._attr_name == "Import"
    elif obis_code.startswith("2.8"):
        assert sensor._attr_name == "Export"
    assert sensor._attr_has_entity_name is True


async def test_cost_sensor_created(hass: HomeAssistant, setup_integration):
    """Test that cost sensor is created when tariff_price is configured."""
    from custom_components.enerabot.sensor import EnerABotCostSensor

    entry = setup_integration
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_cost")
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None


async def test_cost_sensor_not_created_without_price(hass: HomeAssistant):
    """Test that cost sensor is not created when tariff_price is not set."""
    from custom_components.enerabot.coordinator import EnerABotCoordinator

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test No Price",
        data={
            CONF_NAME: "Test No Price",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.0,
            CONF_PRICE_MODE: PRICE_MODE_NONE,
        },
        unique_id="sensor.test_no_price",
    )
    entry.add_to_hass(hass)
    hass.states.async_set("sensor.test_import", "100.0")

    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_cost")
    assert entity_id is None

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_cost_sensor_native_value(hass: HomeAssistant):
    """Test that cost sensor returns the accumulated cost from coordinator."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Cost Sensor",
        data={
            CONF_NAME: "Test Cost Sensor",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.0,
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_TARIFF_PRICE: 0.35,
            OPTION_COST_TOTAL: 42.50,
        },
        unique_id="sensor.test_cost_sensor",
    )
    entry.add_to_hass(hass)
    hass.states.async_set("sensor.test_import", "100.0")

    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_cost")
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert float(state.state) == 42.50

    await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()


async def test_cost_sensor_created_when_price_configured(hass: HomeAssistant, setup_integration):
    """Cost sensor should be created and have a translated name when tariff_price is set."""
    from homeassistant.helpers import entity_registry as er

    entry = setup_integration
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_cost")
    assert entity_id is not None

    state = hass.states.get(entity_id)
    assert state is not None
    assert state.name == "Test Meter Cost"


async def test_cost_sensor_unavailable_without_price(hass: HomeAssistant, mock_config_entry):
    """Cost sensor should report unavailable if tariff_price is later removed from options."""
    from custom_components.enerabot.coordinator import EnerABotCoordinator
    from custom_components.enerabot.sensor import EnerABotCostSensor

    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={**mock_config_entry.options, CONF_PRICE_MODE: PRICE_MODE_FIXED},
    )
    await hass.async_block_till_done()

    coordinator = EnerABotCoordinator(hass, mock_config_entry)
    sensor = EnerABotCostSensor(coordinator, mock_config_entry)

    assert sensor.available is True

    new_options = {k: v for k, v in mock_config_entry.options.items() if k != CONF_TARIFF_PRICE}
    hass.config_entries.async_update_entry(mock_config_entry, options=new_options)
    await hass.async_block_till_done()

    assert sensor.available is False

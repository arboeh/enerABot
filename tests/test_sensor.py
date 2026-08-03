# tests/test_sensor.py

"""Test the enerABot sensor entities."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.enerabot.const import DOMAIN


async def test_sensor_import_created(hass: HomeAssistant, setup_integration):
    """Test that import sensor is created."""
    entry = setup_integration
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_import")

    assert entity_id is not None


async def test_sensor_export_created(hass: HomeAssistant, setup_integration):
    """Test that export sensor is created."""
    entry = setup_integration
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_export")

    assert entity_id is not None


async def test_sensor_import_value(hass: HomeAssistant, setup_integration):
    """Test import sensor value."""
    state = hass.states.get("sensor.test_meter_import")
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

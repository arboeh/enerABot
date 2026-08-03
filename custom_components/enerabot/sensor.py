"""Sensor platform for the enerABot integration."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    CONF_NAME,
    DOMAIN,
    OPTION_LAST_CORRECTION_EXPORT,
    OPTION_LAST_CORRECTION_IMPORT,
    OPTION_OFFSET_EXPORT,
    OPTION_OFFSET_IMPORT,
)
from .coordinator import EnerABotCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enerABot sensors."""
    coordinator: EnerABotCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        EnerABotImportSensor(coordinator, entry),
        EnerABotExportSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class EnerABotImportSensor(CoordinatorEntity, SensorEntity):
    """Sensor for the import energy meter."""

    def __init__(self, coordinator: EnerABotCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_import"
        self._attr_name = f"{entry.title} Import"
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = "kWh"

        meter_name = entry.data.get(CONF_NAME, entry.title)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": meter_name,
            "manufacturer": "enerABot",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("import_value")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        attrs = {}
        offset = self._entry.options.get(OPTION_OFFSET_IMPORT)
        if offset is not None:
            attrs["offset"] = offset
        last_correction = self._entry.options.get(OPTION_LAST_CORRECTION_IMPORT)
        if last_correction is not None:
            attrs["last_correction"] = last_correction
        raw_entity_id = self._entry.data.get(CONF_IMPORT_SENSOR)
        if raw_entity_id is not None:
            attrs["raw_sensor"] = raw_entity_id
        return attrs


class EnerABotExportSensor(CoordinatorEntity, SensorEntity):
    """Sensor for the export energy meter."""

    def __init__(self, coordinator: EnerABotCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_export"
        self._attr_name = f"{entry.title} Export"
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = "kWh"

        meter_name = entry.data.get(CONF_NAME, entry.title)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": meter_name,
            "manufacturer": "enerABot",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        return self.coordinator.data.get("export_value")

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        attrs = {}
        offset = self._entry.options.get(OPTION_OFFSET_EXPORT)
        if offset is not None:
            attrs["offset"] = offset
        last_correction = self._entry.options.get(OPTION_LAST_CORRECTION_EXPORT)
        if last_correction is not None:
            attrs["last_correction"] = last_correction
        raw_entity_id = self._entry.data.get(CONF_EXPORT_SENSOR)
        if raw_entity_id is not None:
            attrs["raw_sensor"] = raw_entity_id
        return attrs

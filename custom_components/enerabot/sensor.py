# custom_components/enerabot/sensor.py

"""Sensor platform for the enerABot integration."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_METER_ID,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    DOMAIN,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
    is_export_obis,
    is_import_obis,
)
from .coordinator import EnerABotCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enerABot sensor."""
    coordinator: EnerABotCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([EnerABotSensor(coordinator, entry)])


class EnerABotSensor(CoordinatorEntity[EnerABotCoordinator], SensorEntity):  # type: ignore[reportIncompatibleVariableOverride]
    """Sensor for the energy meter (import or export, based on OBIS code)."""

    def __init__(self, coordinator: EnerABotCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entry = entry
        obis_code = entry.data[CONF_OBIS_CODE]
        direction = "Import" if is_import_obis(obis_code) else "Export"

        self._attr_unique_id = f"{entry.entry_id}_{direction.lower()}"
        self._attr_name = direction
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
    def native_value(self) -> float | None:  # type: ignore[reportIncompatibleVariableOverride]
        """Return the state."""
        return self.coordinator.data

    @property
    def extra_state_attributes(self) -> dict:  # type: ignore[reportIncompatibleVariableOverride]
        """Return additional attributes."""
        attrs = {}
        offset = self.entry.options.get(OPTION_OFFSET)
        if offset is not None:
            attrs["offset"] = offset
        last_correction = self.entry.options.get(OPTION_LAST_CORRECTION)
        if last_correction is not None:
            attrs["last_correction"] = last_correction
        attrs["raw_sensor"] = self.entry.data[CONF_SENSOR]
        attrs["obis_code"] = self.entry.data[CONF_OBIS_CODE]
        meter_id = self.entry.options.get(CONF_METER_ID)
        if meter_id:
            attrs["meter_id"] = meter_id
        tariff_price = self.entry.options.get(CONF_TARIFF_PRICE)
        if tariff_price:
            attrs["tariff_price"] = tariff_price
        return attrs

"""Number platform for the enerABot integration."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_NAME, CONF_TARIFF_PRICE, DOMAIN, OPTION_OFFSET

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enerABot number entities."""
    async_add_entities(
        [
            EnerABotTariffPriceNumber(hass, entry),
            EnerABotOffsetNumber(hass, entry),
        ]
    )


class EnerABotTariffPriceNumber(NumberEntity):
    """Editable tariff price, grouped under device configuration."""

    _attr_has_entity_name = True
    _attr_translation_key = "tariff_price"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_min_value = 0
    _attr_native_max_value = 9999
    _attr_native_step = 0.001
    _attr_native_unit_of_measurement = "EUR/kWh"
    _attr_mode = NumberMode.BOX

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the tariff price number entity."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_tariff_price"
        meter_name = entry.data.get(CONF_NAME, entry.title)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": meter_name,
            "manufacturer": "enerABot",
        }

    @property
    def native_value(self) -> float | None:  # type: ignore[reportIncompatibleVariableOverride]
        """Return the current tariff price."""
        value = self.entry.options.get(CONF_TARIFF_PRICE)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Update the tariff price from the entity card."""
        new_options = {**self.entry.options, CONF_TARIFF_PRICE: value}
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        LOGGER.info("Tariff price for entry %s set to %s", self.entry.entry_id, value)


class EnerABotOffsetNumber(NumberEntity):
    """Editable offset, grouped under device configuration."""

    _attr_has_entity_name = True
    _attr_translation_key = "offset"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = False
    _attr_native_min_value = -999999
    _attr_native_max_value = 999999
    _attr_native_step = 0.001
    _attr_native_unit_of_measurement = "kWh"
    _attr_mode = NumberMode.BOX

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the offset number entity."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_offset"
        meter_name = entry.data.get(CONF_NAME, entry.title)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": meter_name,
            "manufacturer": "enerABot",
        }

    @property
    def native_value(self) -> float | None:  # type: ignore[reportIncompatibleVariableOverride]
        """Return the current offset."""
        value = self.entry.options.get(OPTION_OFFSET)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Update the offset from the entity card."""
        new_options = {**self.entry.options, OPTION_OFFSET: value}
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        LOGGER.info("Offset for entry %s set to %s", self.entry.entry_id, value)

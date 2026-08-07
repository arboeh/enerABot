"""Select platform for the enerABot integration."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_COST_RESET_CYCLE,
    CONF_PRICE_MODE,
    COST_RESET_NONE,
    COST_RESET_OPTIONS,
    DOMAIN,
    PRICE_MODE_NONE,
    PRICE_MODE_OPTIONS,
    make_device_info,
)

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enerABot select entities."""
    async_add_entities(
        [
            EnerABotPriceModeSelect(hass, entry),
            EnerABotCostResetCycleSelect(hass, entry),
        ]
    )


class EnerABotPriceModeSelect(SelectEntity):
    """Editable price mode, grouped under device configuration."""

    _attr_has_entity_name = True
    _attr_translation_key = "price_mode"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = PRICE_MODE_OPTIONS

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the price mode select entity."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_price_mode"
        self._attr_device_info = make_device_info(entry)

    @property
    def current_option(self) -> str:  # type: ignore[reportIncompatibleVariableOverride]
        """Return the current price mode."""
        return self.entry.options.get(CONF_PRICE_MODE, PRICE_MODE_NONE)

    async def async_select_option(self, option: str) -> None:
        """Update the price mode from the entity card."""
        new_options = {**self.entry.options, CONF_PRICE_MODE: option}
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        LOGGER.info("Price mode for entry %s set to %s", self.entry.entry_id, option)


class EnerABotCostResetCycleSelect(SelectEntity):
    """Editable cost reset cycle, grouped under device configuration."""

    _attr_has_entity_name = True
    _attr_translation_key = "cost_reset_cycle"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = COST_RESET_OPTIONS

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the cost reset cycle select entity."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_cost_reset_cycle"
        self._attr_device_info = make_device_info(entry)

    @property
    def current_option(self) -> str:  # type: ignore[reportIncompatibleVariableOverride]
        """Return the current cost reset cycle."""
        return self.entry.options.get(CONF_COST_RESET_CYCLE, COST_RESET_NONE)

    async def async_select_option(self, option: str) -> None:
        """Update the cost reset cycle from the entity card."""
        new_options = {**self.entry.options, CONF_COST_RESET_CYCLE: option}
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        LOGGER.info(
            "Cost reset cycle for entry %s set to %s",
            self.entry.entry_id,
            option,
        )

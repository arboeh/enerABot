# custom_components/enerabot/button.py

"""Button platform for the enerABot integration."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    OPTION_COST_LAST_ENERGY,
    OPTION_COST_PERIOD_START,
    OPTION_COST_TOTAL,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
    make_device_info,
)

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the enerABot reset button."""
    async_add_entities([EnerABotResetButton(hass, entry)])


class EnerABotResetButton(ButtonEntity):
    """Button to reset offset and cost for a single meter."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the reset button."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_reset"
        self._attr_has_entity_name = True
        self._attr_translation_key = "reset"
        self._attr_device_info = make_device_info(entry)

    async def async_press(self) -> None:
        """Reset offset and cost for this entry."""
        new_options = {
            **self.entry.options,
            OPTION_OFFSET: 0.0,
            OPTION_LAST_CORRECTION: None,
            OPTION_COST_TOTAL: 0.0,
            OPTION_COST_LAST_ENERGY: None,
            OPTION_COST_PERIOD_START: None,
        }
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        LOGGER.info("Reset button pressed for entry %s", self.entry.entry_id)

# custom_components/enerabot/coordinator.py

"""Coordinator for the enerABot integration."""

import logging
from datetime import timedelta

from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_SENSOR,
    DOMAIN,
    OPTION_OFFSET,
    UPDATE_INTERVAL,
)

LOGGER = logging.getLogger(__name__)


class EnerABotCoordinator(DataUpdateCoordinator[float | None]):
    """Class to manage fetching data from the energy meter."""

    def __init__(self, hass, config_entry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.config_entry = config_entry
        self.sensor = config_entry.data[CONF_SENSOR]
        self.unsub_state_changes = None

    async def _async_update_data(self) -> float | None:
        """Fetch data from the sensor and apply the offset."""
        sensor_state = self.hass.states.get(self.sensor)
        if sensor_state is None or sensor_state.state in ("unknown", "unavailable"):
            return None
        try:
            raw_value = float(sensor_state.state)
        except (ValueError, TypeError):
            return None
        offset = self.config_entry.options.get(OPTION_OFFSET, 0.0)
        try:
            offset = float(offset)
        except (ValueError, TypeError):
            offset = 0.0
        return round(raw_value + offset, 3)

    async def async_start_state_listener(self) -> None:
        """Start listening for state changes on the source sensor."""
        if self.unsub_state_changes:
            return
        self.unsub_state_changes = async_track_state_change_event(
            self.hass,
            [self.sensor],
            self._handle_state_change,
        )
        LOGGER.info("Started state change listener for sensor %s", self.sensor)

    async def _handle_state_change(self, event) -> None:
        """Handle state change events from the source sensor."""
        LOGGER.debug("Sensor state changed: %s", event.data.get("entity_id"))
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self.unsub_state_changes:
            self.unsub_state_changes()
            self.unsub_state_changes = None

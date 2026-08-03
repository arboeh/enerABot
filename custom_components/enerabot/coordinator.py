"""Coordinator for the enerABot integration."""

import logging
from datetime import timedelta

from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    DOMAIN,
    OPTION_OFFSET_EXPORT,
    OPTION_OFFSET_IMPORT,
    UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class EnerABotCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the energy meters."""

    # No switch.py is needed: enerABot only manages sensor offset
    # corrections via services and options flow. There are no
    # switchable actuators in this integration. A toggle for
    # pausing offset correction would add unnecessary complexity
    # for a feature that can be achieved by simply removing the
    # offset value from the config entry options.

    def __init__(self, hass, config_entry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.config_entry = config_entry

        self._import_sensor = config_entry.data.get(CONF_IMPORT_SENSOR)
        self._export_sensor = config_entry.data.get(CONF_EXPORT_SENSOR)

        self._unsub_state_changes = None

    async def _async_update_data(self) -> dict[str, float | None]:
        """Fetch data from the sensors and apply offsets.

        Returns None for a sensor when it is unavailable or unparseable
        instead of raising UpdateFailed. This preserves the last known
        value in the sensor entity and keeps TOTAL_INCREASING statistics
        intact, avoiding gaps in the energy statistics history.
        """
        import_sensor_state = self.hass.states.get(self._import_sensor) if self._import_sensor else None
        export_sensor_state = self.hass.states.get(self._export_sensor) if self._export_sensor else None

        import_value = self._apply_offset(import_sensor_state, OPTION_OFFSET_IMPORT)
        export_value = self._apply_offset(export_sensor_state, OPTION_OFFSET_EXPORT)

        return {
            "import_value": import_value,
            "export_value": export_value,
        }

    def _apply_offset(self, sensor_state, option_key: str) -> float | None:
        """Apply the stored offset to a sensor state."""
        if sensor_state is None or sensor_state.state in ("unknown", "unavailable"):
            return None

        try:
            raw_value = float(sensor_state.state)
        except (ValueError, TypeError):
            return None

        offset = self.config_entry.options.get(option_key, 0.0)
        try:
            offset = float(offset)
        except (ValueError, TypeError):
            offset = 0.0

        return round(raw_value + offset, 3)

    async def async_start_state_listener(self) -> None:
        """Start listening for state changes on the source sensors."""
        if self._unsub_state_changes:
            return

        sensors = []
        if self._import_sensor:
            sensors.append(self._import_sensor)
        if self._export_sensor:
            sensors.append(self._export_sensor)

        if not sensors:
            return

        self._unsub_state_changes = async_track_state_change_event(
            self.hass,
            sensors,
            self._handle_state_change,
        )
        _LOGGER.info("Started state change listener for sensors: %s", sensors)

    async def _handle_state_change(self, event) -> None:
        """Handle state change events from source sensors."""
        _LOGGER.debug("Sensor state changed: %s", event.data.get("entity_id"))
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._unsub_state_changes:
            self._unsub_state_changes()
            self._unsub_state_changes = None

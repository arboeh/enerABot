# custom_components/enerabot/coordinator.py

"""Coordinator for the enerABot integration."""

import inspect
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_COST_RESET_CYCLE,
    CONF_PRICE_MODE,
    CONF_PRICE_SENSOR,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    COST_RESET_MONTHLY,
    COST_RESET_NONE,
    COST_RESET_YEARLY,
    DOMAIN,
    OPTION_COST_LAST_ENERGY,
    OPTION_COST_PERIOD_START,
    OPTION_COST_TOTAL,
    OPTION_OFFSET,
    PRICE_MODE_DYNAMIC,
    PRICE_MODE_FIXED,
    PRICE_MODE_NONE,
    UPDATE_INTERVAL,
)

LOGGER = logging.getLogger(__name__)


class EnerABotCoordinator(DataUpdateCoordinator[float | None]):
    """Class to manage fetching data from the energy meter."""

    def __init__(self, hass, config_entry) -> None:
        """Initialize the coordinator."""
        kwargs: dict[str, Any] = {
            "name": DOMAIN,
            "update_interval": timedelta(seconds=UPDATE_INTERVAL),
        }
        if "config_entry" in inspect.signature(DataUpdateCoordinator.__init__).parameters:
            kwargs["config_entry"] = config_entry
        super().__init__(
            hass,
            LOGGER,
            **kwargs,
        )
        self.config_entry = config_entry
        self.sensor = config_entry.data[CONF_SENSOR]
        self.unsub_state_changes = None
        self._cost_total: float | None = config_entry.options.get(OPTION_COST_TOTAL)
        self._cost_period_start: str | None = config_entry.options.get(OPTION_COST_PERIOD_START)
        self._cost_last_energy: float | None = config_entry.options.get(OPTION_COST_LAST_ENERGY)
        self._cost_price: float | None = None

    def _calculate_offset_value(self) -> float | None:
        """Calculate the energy value with offset applied."""
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

    async def _async_update_data(self) -> float | None:
        """Fetch data from the sensor and apply the offset."""
        value = self._calculate_offset_value()
        if value is not None:
            await self._update_cost(value)
        return value

    @property
    def cost_total(self) -> float | None:
        """Return the accumulated cost for the current period."""
        return self._cost_total

    def _get_current_price(self) -> float | None:
        """Return the current price per kWh, from fixed or dynamic source."""
        price_mode = self.config_entry.options.get(CONF_PRICE_MODE, PRICE_MODE_NONE)
        if price_mode == PRICE_MODE_FIXED:
            price = self.config_entry.options.get(CONF_TARIFF_PRICE)
            try:
                return float(price) if price is not None else None
            except (ValueError, TypeError):
                return None
        if price_mode == PRICE_MODE_DYNAMIC:
            sensor_id = self.config_entry.options.get(CONF_PRICE_SENSOR)
            if not sensor_id:
                return None
            state = self.hass.states.get(sensor_id)
            if state is None or state.state in ("unknown", "unavailable"):
                return None
            try:
                return float(state.state)
            except (ValueError, TypeError):
                return None
        return None

    async def _update_cost(self, current_energy: float) -> None:
        """Update accumulated cost incrementally, respecting the reset cycle."""
        price = self._get_current_price()
        if price is None:
            return

        now = datetime.now(UTC)
        period_start_iso = self._cost_period_start
        reset_cycle = self.config_entry.options.get(CONF_COST_RESET_CYCLE, COST_RESET_NONE)
        last_energy = self._cost_last_energy if self._cost_last_energy is not None else current_energy
        cost_total = self._cost_total if self._cost_total is not None else 0.0

        needs_reset = False
        if reset_cycle != COST_RESET_NONE and period_start_iso:
            period_start = datetime.fromisoformat(period_start_iso)
            if reset_cycle == COST_RESET_MONTHLY and (now.year != period_start.year or now.month != period_start.month):
                needs_reset = True
            elif reset_cycle == COST_RESET_YEARLY and now.year != period_start.year:
                needs_reset = True

        if needs_reset or not period_start_iso:
            cost_total = 0.0
            last_energy = current_energy
            period_start_iso = now.isoformat()

        delta_energy = max(current_energy - last_energy, 0)
        cost_total = round(cost_total + delta_energy * price, 2)

        self._cost_total = cost_total
        self._cost_last_energy = current_energy
        self._cost_period_start = period_start_iso

    async def async_start_state_listener(self) -> None:
        """Start listening for state changes on the source sensor and price sensor."""
        if self.unsub_state_changes:
            return
        sensors = [self.sensor]
        price_sensor = self.config_entry.options.get(CONF_PRICE_SENSOR)
        if price_sensor:
            sensors.append(price_sensor)
        self.unsub_state_changes = async_track_state_change_event(
            self.hass,
            sensors,
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

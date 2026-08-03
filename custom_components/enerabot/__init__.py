"""The enerABot integration."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    DOMAIN,
    OPTION_LAST_CORRECTION_EXPORT,
    OPTION_LAST_CORRECTION_IMPORT,
    OPTION_OFFSET_EXPORT,
    OPTION_OFFSET_IMPORT,
)
from .coordinator import EnerABotCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the enerABot component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up enerABot from a config entry."""
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        _LOGGER.debug("Entry %s already set up, skipping", entry.entry_id)
        return True

    hass.data.setdefault(DOMAIN, {})

    coordinator = EnerABotCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        _LOGGER.warning(
            "Sensor not ready during setup of %s, will retry on next update",
            entry.entry_id,
        )
        raise

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await coordinator.async_start_state_listener()

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _register_services(hass)

    return True


def _register_services(hass: HomeAssistant) -> None:
    """Register enerABot services."""
    if hass.services.has_service(DOMAIN, "set_energy_meter_import"):
        return

    async def handle_set_energy_meter_import(call: ServiceCall) -> None:
        """Handle set_energy_meter_import service call."""
        entity_id = call.data["entity_id"]
        meter_value = call.data["meter_value"]

        await _calculate_and_store_offset(hass, entity_id, meter_value, is_import=True)

    async def handle_set_energy_meter_export(call: ServiceCall) -> None:
        """Handle set_energy_meter_export service call."""
        entity_id = call.data["entity_id"]
        meter_value = call.data["meter_value"]

        await _calculate_and_store_offset(hass, entity_id, meter_value, is_import=False)

    hass.services.async_register(
        DOMAIN,
        "set_energy_meter_import",
        handle_set_energy_meter_import,
    )

    hass.services.async_register(
        DOMAIN,
        "set_energy_meter_export",
        handle_set_energy_meter_export,
    )

    _LOGGER.info("Registered enerABot services")


async def _calculate_and_store_offset(
    hass: HomeAssistant,
    entity_id: str,
    meter_value: float,
    is_import: bool,
) -> None:
    """Calculate and store the offset for a meter."""
    entries = hass.config_entries.async_entries(DOMAIN)
    for entry in entries:
        import_sensor_id = entry.data.get(CONF_IMPORT_SENSOR)
        export_sensor_id = entry.data.get(CONF_EXPORT_SENSOR)

        target_sensor = import_sensor_id if is_import else export_sensor_id

        if target_sensor != entity_id:
            continue

        current_value = hass.states.get(entity_id)
        if current_value is None or current_value.state in ("unknown", "unavailable"):
            _LOGGER.warning(
                "Cannot calculate offset for %s: sensor state is %s",
                entity_id,
                current_value.state if current_value else "None",
            )
            return

        try:
            current = float(current_value.state)
        except (ValueError, TypeError):
            _LOGGER.warning("Cannot parse sensor state for %s: %s", entity_id, current_value.state)
            return

        offset = round(meter_value - current, 3)
        now_iso = datetime.now(UTC).isoformat()

        sensor_key = OPTION_OFFSET_IMPORT if is_import else OPTION_OFFSET_EXPORT
        correction_key = OPTION_LAST_CORRECTION_IMPORT if is_import else OPTION_LAST_CORRECTION_EXPORT

        new_options = {
            **entry.options,
            sensor_key: offset,
            correction_key: now_iso,
        }

        await hass.config_entries.async_update_options(entry, new_options)

        _LOGGER.info(
            "Offset for %s (%s) set to %s (meter_value=%s, current=%s)",
            entity_id,
            "import" if is_import else "export",
            offset,
            meter_value,
            current,
        )
        return

    _LOGGER.warning("No matching config entry found for entity %s", entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
            hass.services.async_remove(DOMAIN, "set_energy_meter_import")
            hass.services.async_remove(DOMAIN, "set_energy_meter_export")
            _LOGGER.info("Unregistered enerABot services")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

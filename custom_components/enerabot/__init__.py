# custom_components/enerabot/__init__.py

"""The enerABot integration."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_SENSOR,
    DOMAIN,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
)
from .coordinator import EnerABotCoordinator

LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the enerABot component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up enerABot from a config entry."""
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        LOGGER.debug("Entry %s already set up, skipping", entry.entry_id)
        return True

    hass.data.setdefault(DOMAIN, {})

    coordinator = EnerABotCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        LOGGER.warning(
            "Sensor not ready during setup of %s, will retry on next update",
            entry.entry_id,
        )
        raise

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    await coordinator.async_start_state_listener()

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    register_services(hass)

    return True


def register_services(hass: HomeAssistant) -> None:
    """Register enerABot services."""
    if hass.services.has_service(DOMAIN, "set_energy_meter"):
        return

    async def handle_set_energy_meter(call: ServiceCall) -> None:
        """Handle set_energy_meter service call."""
        entity_id = call.data["entity_id"]
        meter_value = call.data["meter_value"]

        await calculate_and_store_offset(hass, entity_id, meter_value)

    hass.services.async_register(
        DOMAIN,
        "set_energy_meter",
        handle_set_energy_meter,
    )

    LOGGER.info("Registered enerABot services")


async def calculate_and_store_offset(
    hass: HomeAssistant,
    entity_id: str,
    meter_value: float,
) -> None:
    """Calculate and store the offset for a meter."""
    entries = hass.config_entries.async_entries(DOMAIN)
    for entry in entries:
        if entry.data.get(CONF_SENSOR) != entity_id:
            continue

        current_value = hass.states.get(entity_id)
        if current_value is None or current_value.state in ("unknown", "unavailable"):
            LOGGER.warning(
                "Cannot calculate offset for %s: sensor state is %s",
                entity_id,
                current_value.state if current_value else None,
            )
            return

        try:
            current = float(current_value.state)
        except (ValueError, TypeError):
            LOGGER.warning("Cannot parse sensor state for %s: %s", entity_id, current_value.state)
            return

        offset = round(meter_value - current, 3)
        now_iso = datetime.now(UTC).isoformat()

        new_options = {
            **entry.options,
            OPTION_OFFSET: offset,
            OPTION_LAST_CORRECTION: now_iso,
        }

        hass.config_entries.async_update_entry(entry, options=new_options)

        LOGGER.info(
            "Offset for %s (%s) set to %s (meter=%s, current=%s)",
            entity_id,
            entry.data[CONF_OBIS_CODE],
            offset,
            meter_value,
            current,
        )
        return

    LOGGER.warning("No matching config entry found for entity %s", entity_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old dual-sensor entries (version 1) to single-sensor entries (version 2)."""
    if entry.version == 1 and "import_sensor" in entry.data:
        LOGGER.info("Migrating enerABot entry %s to version 2", entry.entry_id)
        import_sensor = entry.data.get("import_sensor")
        export_sensor = entry.data.get("export_sensor")

        if import_sensor:
            hass.config_entries.async_update_entry(
                entry,
                data={CONF_NAME: entry.data[CONF_NAME], CONF_SENSOR: import_sensor, CONF_OBIS_CODE: "1.8.2"},
                options={
                    OPTION_OFFSET: entry.options.get("offset_import", 0.0),
                    OPTION_LAST_CORRECTION: entry.options.get("last_correction_import"),
                },
                version=2,
            )
        if export_sensor and not import_sensor:
            hass.config_entries.async_update_entry(
                entry,
                data={CONF_NAME: entry.data[CONF_NAME], CONF_SENSOR: export_sensor, CONF_OBIS_CODE: "2.8.2"},
                options={
                    OPTION_OFFSET: entry.options.get("offset_export", 0.0),
                    OPTION_LAST_CORRECTION: entry.options.get("last_correction_export"),
                },
                version=2,
            )
        elif export_sensor and import_sensor:
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN,
                    context={"source": "import"},
                    data={
                        CONF_NAME: f"{entry.data[CONF_NAME]} Export",
                        CONF_SENSOR: export_sensor,
                        CONF_OBIS_CODE: "2.8.2",
                    },
                )
            )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
            hass.services.async_remove(DOMAIN, "set_energy_meter")
            LOGGER.info("Unregistered enerABot services")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

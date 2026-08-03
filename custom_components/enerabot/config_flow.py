# custom_components/enerabot/config_flow.py

"""Config flow for the enerABot integration."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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
from .options_flow import EnerABotOptionsFlow

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Optional(CONF_IMPORT_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="sensor",
                multiple=False,
            )
        ),
        vol.Optional("initial_import_meter_value"): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=999999,
                step=1,
                unit_of_measurement="kWh",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Optional(CONF_EXPORT_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="sensor",
                multiple=False,
            )
        ),
        vol.Optional("initial_export_meter_value"): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=999999,
                step=1,
                unit_of_measurement="kWh",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
    }
)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to proceed."""
    import_sensor = data.get(CONF_IMPORT_SENSOR)
    export_sensor = data.get(CONF_EXPORT_SENSOR)

    if not import_sensor and not export_sensor:
        raise CannotConnect("At least one of import or export sensor is required")

    for entity_id in (import_sensor, export_sensor):
        if entity_id is None:
            continue
        state = hass.states.get(entity_id)
        if state is None:
            raise CannotConnect(f"Entity {entity_id} not found")
        if state.state in ("unknown", "unavailable"):
            raise CannotConnect(f"Entity {entity_id} state is {state.state}")
        try:
            float(state.state)
        except (ValueError, TypeError):
            raise CannotConnect(f"Entity {entity_id} has non-numeric state") from None

    return {
        "title": data[CONF_NAME],
        "import_sensor": import_sensor,
        "export_sensor": export_sensor,
    }


class EnerABotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for enerABot."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                unique_id = f"{info.get('import_sensor') or 'none'}_{info.get('export_sensor') or 'none'}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                options: dict[str, Any] = {}
                now_iso = datetime.now(UTC).isoformat()

                if info["import_sensor"] and user_input.get("initial_import_meter_value") is not None:
                    current_state = self.hass.states.get(info["import_sensor"])
                    if current_state and current_state.state not in ("unknown", "unavailable"):
                        try:
                            current = float(current_state.state)
                            options[OPTION_OFFSET_IMPORT] = round(user_input["initial_import_meter_value"] - current, 3)
                            options[OPTION_LAST_CORRECTION_IMPORT] = now_iso
                        except (ValueError, TypeError):
                            pass

                if info["export_sensor"] and user_input.get("initial_export_meter_value") is not None:
                    current_state = self.hass.states.get(info["export_sensor"])
                    if current_state and current_state.state not in ("unknown", "unavailable"):
                        try:
                            current = float(current_state.state)
                            options[OPTION_OFFSET_EXPORT] = round(user_input["initial_export_meter_value"] - current, 3)
                            options[OPTION_LAST_CORRECTION_EXPORT] = now_iso
                        except (ValueError, TypeError):
                            pass

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                    options=options,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> EnerABotOptionsFlow:
        """Get the options flow for this handler."""
        return EnerABotOptionsFlow(config_entry)

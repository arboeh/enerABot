# custom_components/enerabot/config_flow.py

"""Config flow for the enerABot integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_EXPORT_SENSOR, CONF_IMPORT_SENSOR, CONF_NAME, DOMAIN
from .options_flow import EnerABotOptionsFlow

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_IMPORT_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="sensor",
                multiple=False,
            )
        ),
        vol.Required(CONF_EXPORT_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="sensor",
                multiple=False,
            )
        ),
    }
)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to proceed."""
    import_sensor = data[CONF_IMPORT_SENSOR]
    export_sensor = data[CONF_EXPORT_SENSOR]

    for entity_id in (import_sensor, export_sensor):
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
                unique_id = f"{info['import_sensor']}_{info['export_sensor']}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        **user_input,
                    },
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

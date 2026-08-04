# custom_components/enerabot/config_flow.py

"""Config flow for the enerABot integration."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

try:
    from homeassistant.config_entries import ConfigFlowResult
except ImportError:  # pragma: no cover - older HA versions
    from homeassistant.data_entry_flow import FlowResult as ConfigFlowResult

from .const import (
    CONF_METER_ID,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_READING_CYCLE,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    DOMAIN,
    OBIS_CODE_OPTIONS,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
    READING_CYCLE_MANUAL,
    READING_CYCLE_OPTIONS,
    is_export_obis,
    is_import_obis,
)
from .options_flow import EnerABotOptionsFlow

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor", multiple=False)
        ),
        vol.Required(CONF_OBIS_CODE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=OBIS_CODE_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
                custom_value=True,
            )
        ),
        vol.Optional("initial_meter_value"): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=999999,
                step=1,
                unit_of_measurement="kWh",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Optional(CONF_METER_ID): str,
        vol.Optional(CONF_TARIFF_PRICE): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=9999,
                step=0.001,
                unit_of_measurement="EUR/kWh",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Optional(CONF_READING_CYCLE, default=READING_CYCLE_MANUAL): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=READING_CYCLE_OPTIONS,
                mode=selector.SelectSelectorMode.DROPDOWN,
                translation_key="reading_cycle",
            )
        ),
    }
)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to proceed."""
    sensor = data[CONF_SENSOR]
    obis_code = data[CONF_OBIS_CODE]

    if not (is_import_obis(obis_code) or is_export_obis(obis_code)):
        raise CannotConnect(f"OBIS code {obis_code} is neither import (1.8.x) nor export (2.8.x)")

    state = hass.states.get(sensor)
    if state is None:
        raise CannotConnect(f"Entity {sensor} not found")
    if state.state in ("unknown", "unavailable"):
        raise CannotConnect(f"Entity {sensor} state is {state.state}")
    try:
        float(state.state)
    except (ValueError, TypeError) as err:
        raise CannotConnect(f"Entity {sensor} has non-numeric state") from err

    return {
        "title": data[CONF_NAME],
        "sensor": sensor,
        "obis_code": obis_code,
    }


class EnerABotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for enerABot."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
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
                await self.async_set_unique_id(info["sensor"])
                self._abort_if_unique_id_configured()

                options: dict[str, Any] = {}
                now_iso = datetime.now(UTC).isoformat()

                sensor_entity_id = info["sensor"]
                current_state = self.hass.states.get(sensor_entity_id)
                if (
                    current_state
                    and current_state.state not in ("unknown", "unavailable")
                    and user_input.get("initial_meter_value") is not None
                ):
                    try:
                        current = float(current_state.state)
                        options[OPTION_OFFSET] = round(user_input["initial_meter_value"] - current, 3)
                        options[OPTION_LAST_CORRECTION] = now_iso
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

    async def async_step_import(self, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Handle import of a config entry from a migration or YAML."""
        return await self.async_step_user(user_input)

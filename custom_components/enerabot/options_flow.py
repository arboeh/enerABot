# custom_components/enerabot/options_flow.py

"""Options flow for the enerABot integration."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    OPTION_LAST_CORRECTION_EXPORT,
    OPTION_LAST_CORRECTION_IMPORT,
    OPTION_OFFSET_EXPORT,
    OPTION_OFFSET_IMPORT,
)

_LOGGER = logging.getLogger(__name__)


class EnerABotOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for enerABot."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options - main menu."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        menu_options: list[str] = []
        if self._config_entry.data.get(CONF_IMPORT_SENSOR):
            menu_options.append("import")
        if self._config_entry.data.get(CONF_EXPORT_SENSOR):
            menu_options.append("export")
        return self.async_show_menu(
            step_id="init",
            menu_options=menu_options,
        )

    async def async_step_import(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Correct the import meter offset."""
        errors: dict[str, str] = {}

        if user_input is not None:
            meter_value = user_input["meter_value"]
            sensor_entity_id = self._config_entry.data.get(CONF_IMPORT_SENSOR)

            if sensor_entity_id is None:
                return self.async_abort(reason="no_sensor")

            current_state = self.hass.states.get(sensor_entity_id)
            if current_state is None or current_state.state in ("unknown", "unavailable"):
                errors["base"] = "sensor_unavailable"
                return self.async_show_form(
                    step_id="import",
                    data_schema=vol.Schema(
                        {
                            vol.Required("meter_value"): selector.NumberSelector(
                                selector.NumberSelectorConfig(
                                    min=0,
                                    max=999999,
                                    step=1,
                                    unit_of_measurement="kWh",
                                    mode=selector.NumberSelectorMode.BOX,
                                )
                            ),
                        }
                    ),
                    errors=errors,
                )

            try:
                current = float(current_state.state)
            except (ValueError, TypeError):
                errors["base"] = "sensor_unavailable"
                return self.async_show_form(
                    step_id="import",
                    data_schema=vol.Schema(
                        {
                            vol.Required("meter_value"): selector.NumberSelector(
                                selector.NumberSelectorConfig(
                                    min=0,
                                    max=999999,
                                    step=1,
                                    unit_of_measurement="kWh",
                                    mode=selector.NumberSelectorMode.BOX,
                                )
                            ),
                        }
                    ),
                    errors=errors,
                )

            offset = round(meter_value - current, 3)

            now_iso = datetime.now(UTC).isoformat()

            new_options = {
                **self._config_entry.options,
                OPTION_OFFSET_IMPORT: offset,
                OPTION_LAST_CORRECTION_IMPORT: now_iso,
            }

            self.hass.config_entries.async_update_entry(self._config_entry, options=new_options)

            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="import",
            data_schema=vol.Schema(
                {
                    vol.Required("meter_value"): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=999999,
                            step=1,
                            unit_of_measurement="kWh",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_export(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Correct the export meter offset."""
        errors: dict[str, str] = {}

        if user_input is not None:
            meter_value = user_input["meter_value"]
            sensor_entity_id = self._config_entry.data.get(CONF_EXPORT_SENSOR)

            if sensor_entity_id is None:
                return self.async_abort(reason="no_sensor")

            current_state = self.hass.states.get(sensor_entity_id)
            if current_state is None or current_state.state in ("unknown", "unavailable"):
                errors["base"] = "sensor_unavailable"
                return self.async_show_form(
                    step_id="export",
                    data_schema=vol.Schema(
                        {
                            vol.Required("meter_value"): selector.NumberSelector(
                                selector.NumberSelectorConfig(
                                    min=0,
                                    max=999999,
                                    step=1,
                                    unit_of_measurement="kWh",
                                    mode=selector.NumberSelectorMode.BOX,
                                )
                            ),
                        }
                    ),
                    errors=errors,
                )

            try:
                current = float(current_state.state)
            except (ValueError, TypeError):
                errors["base"] = "sensor_unavailable"
                return self.async_show_form(
                    step_id="export",
                    data_schema=vol.Schema(
                        {
                            vol.Required("meter_value"): selector.NumberSelector(
                                selector.NumberSelectorConfig(
                                    min=0,
                                    max=999999,
                                    step=1,
                                    unit_of_measurement="kWh",
                                    mode=selector.NumberSelectorMode.BOX,
                                )
                            ),
                        }
                    ),
                    errors=errors,
                )

            offset = round(meter_value - current, 3)

            now_iso = datetime.now(UTC).isoformat()

            new_options = {
                **self._config_entry.options,
                OPTION_OFFSET_EXPORT: offset,
                OPTION_LAST_CORRECTION_EXPORT: now_iso,
            }

            self.hass.config_entries.async_update_entry(self._config_entry, options=new_options)

            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="export",
            data_schema=vol.Schema(
                {
                    vol.Required("meter_value"): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=999999,
                            step=1,
                            unit_of_measurement="kWh",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
            errors=errors,
        )

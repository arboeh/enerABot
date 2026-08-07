# custom_components/enerabot/options_flow.py

"""Options flow for the enerABot integration."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

try:
    from homeassistant.config_entries import ConfigFlowResult
except ImportError:  # pragma: no cover - older HA versions
    from homeassistant.data_entry_flow import FlowResult as ConfigFlowResult

from .const import (
    CONF_COST_RESET_CYCLE,
    CONF_METER_ID,
    CONF_OBIS_CODE,
    CONF_PRICE_MODE,
    CONF_PRICE_SENSOR,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    COST_RESET_NONE,
    COST_RESET_OPTIONS,
    DOMAIN,
    ENERGY_SENSOR_DEVICE_CLASSES,
    OBIS_CODE_OPTIONS,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
    PRICE_MODE_NONE,
    PRICE_MODE_OPTIONS,
    PRICE_SENSOR_DEVICE_CLASSES,
)

_LOGGER = logging.getLogger(__name__)


class EnerABotOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for enerABot."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    def build_meter_correction_schema(self) -> vol.Schema:
        """Build schema for meter correction with metadata fields."""
        sensor = self._config_entry.data[CONF_SENSOR]
        offset = self._config_entry.options.get(OPTION_OFFSET, 0.0)
        state = self.hass.states.get(sensor)
        current_meter_value = 0.0
        if state is not None and state.state not in ("unknown", "unavailable"):
            try:
                current_meter_value = round(float(state.state) + float(offset), 3)
            except (ValueError, TypeError):
                current_meter_value = 0.0

        current_meter_id = self._config_entry.options.get(CONF_METER_ID, "")
        current_obis = self._config_entry.options.get(CONF_OBIS_CODE)
        current_price = self._config_entry.options.get(CONF_TARIFF_PRICE, 0.0)
        current_price_mode = self._config_entry.options.get(CONF_PRICE_MODE, PRICE_MODE_NONE)
        current_price_sensor = self._config_entry.options.get(CONF_PRICE_SENSOR)
        current_cost_reset = self._config_entry.options.get(CONF_COST_RESET_CYCLE, COST_RESET_NONE)

        # Fall back to data-level values for fields that may still live in data
        if not current_obis:
            current_obis = self._config_entry.data.get(CONF_OBIS_CODE, "")
        if not current_price:
            current_price = self._config_entry.data.get(CONF_TARIFF_PRICE, 0.0)

        schema_entries: dict[Any, Any] = {
            vol.Required("meter_value", default=current_meter_value): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=999999,
                    step=1,
                    unit_of_measurement="kWh",
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_METER_ID, default=current_meter_id): str,
            vol.Optional(CONF_OBIS_CODE, default=current_obis): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=OBIS_CODE_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True,
                )
            ),
            vol.Optional(CONF_COST_RESET_CYCLE, default=current_cost_reset): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=COST_RESET_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="cost_reset_cycle",
                )
            ),
            vol.Optional(CONF_PRICE_MODE, default=current_price_mode): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=PRICE_MODE_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    translation_key="price_mode",
                )
            ),
        }

        if current_price_sensor:
            schema_entries[vol.Optional(CONF_PRICE_SENSOR, default=current_price_sensor)] = selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="sensor",
                    device_class=PRICE_SENSOR_DEVICE_CLASSES,
                    multiple=False,
                )
            )
        else:
            schema_entries[vol.Optional(CONF_PRICE_SENSOR)] = selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain="sensor",
                    device_class=PRICE_SENSOR_DEVICE_CLASSES,
                    multiple=False,
                )
            )

        schema_entries[vol.Optional(CONF_TARIFF_PRICE, default=current_price)] = selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0,
                max=9999,
                step=0.001,
                unit_of_measurement="EUR/kWh",
                mode=selector.NumberSelectorMode.BOX,
            )
        )

        return vol.Schema(schema_entries)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage the options - main menu."""
        errors: dict[str, str] = {}
        if user_input is not None:
            meter_value = user_input.pop("meter_value")
            sensor = self._config_entry.data[CONF_SENSOR]
            current_state = self.hass.states.get(sensor)

            if current_state is None or current_state.state in (
                "unknown",
                "unavailable",
            ):
                errors["base"] = "cannot_connect"
            else:
                try:
                    current = float(current_state.state)
                except (ValueError, TypeError):
                    errors["base"] = "cannot_connect"
                else:
                    user_input[OPTION_OFFSET] = round(meter_value - current, 3)
                    user_input[OPTION_LAST_CORRECTION] = datetime.now(UTC).isoformat()
                    return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.build_meter_correction_schema(),
            errors=errors,
        )

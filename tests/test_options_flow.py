"""Tests for the enerABot options flow."""

from datetime import datetime, timezone
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_COST_RESET_CYCLE,
    CONF_METER_ID,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_PRICE_MODE,
    CONF_PRICE_SENSOR,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    COST_RESET_NONE,
    DOMAIN,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
    PRICE_MODE_DYNAMIC,
    PRICE_MODE_FIXED,
    PRICE_MODE_NONE,
)


async def test_options_flow_calculates_new_offset(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that entering a meter value recalculates the offset."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    assert result["type"] == FlowResultType.FORM

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "meter_value": 150.0,
            CONF_METER_ID: "1SAG1234567890",
            CONF_OBIS_CODE: "1.8.2",
            CONF_TARIFF_PRICE: 0.32,
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_COST_RESET_CYCLE: COST_RESET_NONE,
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[OPTION_OFFSET] == 50.0
    assert OPTION_LAST_CORRECTION in mock_config_entry.options


async def test_options_flow_recalculates_after_reset(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that a new meter value works after a previous reset (offset=0)."""
    hass.states.async_set("sensor.test_import", "0.0")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "meter_value": 42.0,
            CONF_METER_ID: "1SAG1234567890",
            CONF_OBIS_CODE: "1.8.2",
            CONF_TARIFF_PRICE: 0.32,
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_COST_RESET_CYCLE: COST_RESET_NONE,
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[OPTION_OFFSET] == 42.0


async def test_options_flow_cannot_connect_on_unavailable_sensor(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that an unavailable source sensor produces a form error."""
    hass.states.async_set("sensor.test_import", "unavailable")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"meter_value": 42.0},
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_options_flow_cannot_connect_on_unknown_sensor(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that an unknown source sensor produces a form error."""
    hass.states.async_set("sensor.test_import", "unknown")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"meter_value": 42.0},
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_options_flow_cannot_connect_on_nonexistent_sensor(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that a missing source sensor produces a form error."""
    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"meter_value": 42.0},
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_options_flow_meter_value_not_persisted_as_option(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that meter_value itself is never stored as a config option."""
    hass.states.async_set("sensor.test_import", "10.0")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"meter_value": 20.0},
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert "meter_value" not in mock_config_entry.options


async def test_options_flow_preserves_other_options(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that existing options are preserved when recalibrating."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "meter_value": 150.0,
            CONF_METER_ID: "1SAG1234567890",
            CONF_OBIS_CODE: "1.8.2",
            CONF_TARIFF_PRICE: 0.35,
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_COST_RESET_CYCLE: COST_RESET_NONE,
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[OPTION_OFFSET] == 50.0
    assert mock_config_entry.options[CONF_TARIFF_PRICE] == 0.35
    assert mock_config_entry.options[CONF_PRICE_MODE] == PRICE_MODE_FIXED


async def test_options_flow_last_correction_is_iso_timestamp(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that last_correction is a valid ISO-format timestamp."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"meter_value": 150.0},
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    correction_str = mock_config_entry.options[OPTION_LAST_CORRECTION]
    parsed = datetime.fromisoformat(correction_str)
    assert parsed.tzinfo is not None


async def test_options_flow_negative_offset(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that entering a value below current sensor reading produces a negative offset."""
    hass.states.async_set("sensor.test_import", "200.0")

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )
    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"meter_value": 180.0},
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options[OPTION_OFFSET] == -20.0


async def test_options_flow_prefills_current_meter_value(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test that the form pre-fills meter_value with source plus offset."""
    hass.states.async_set("sensor.test_import", "900.0")
    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={
            **mock_config_entry.options,
            OPTION_OFFSET: 20.0,
        },
    )

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )

    assert result["data_schema"] is not None
    schema = result["data_schema"].schema
    meter_value_key = next(k for k in schema if str(k) == "meter_value")
    assert meter_value_key.default() == 920.0


def test_options_schema_field_order_matches_entity_sort_order(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Options dialog field order must follow the entity display order."""
    from custom_components.enerabot.options_flow import EnerABotOptionsFlow

    flow = EnerABotOptionsFlow(mock_config_entry)
    flow.hass = hass
    schema = flow.build_meter_correction_schema()

    field_names = [str(key) for key in schema.schema]
    expected_order = [
        "meter_value",
        "meter_id",
        "obis_code",
        "cost_reset_cycle",
        "price_mode",
        "price_sensor",
        "tariff_price",
    ]
    assert field_names == expected_order


async def test_price_sensor_selector_in_options_flow_filters_monetary(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that the price_sensor EntitySelector in options flow filters by 'monetary' device class.

    The default mock_config_entry has no CONF_PRICE_SENSOR in options or data,
    so the 'without default' branch of build_meter_correction_schema is exercised.
    Both branches apply the same device_class filter.
    """
    from custom_components.enerabot.options_flow import EnerABotOptionsFlow

    flow = EnerABotOptionsFlow(mock_config_entry)
    flow.hass = hass
    schema = flow.build_meter_correction_schema()

    schema_dict = schema.schema
    price_sensor_key = next(k for k in schema_dict if k == CONF_PRICE_SENSOR)
    selector_config = schema_dict[price_sensor_key].config
    assert selector_config["device_class"] == ["monetary"]


async def test_options_flow_with_price_sensor_preserves_functionality(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Regression test: options flow with a configured price sensor still works.

    Ensures the device_class filter on the price_sensor EntitySelector does not
    break the dynamic price mode options flow when a valid price sensor is set.
    """
    hass.states.async_set("sensor.test_import", "100.0")
    hass.states.async_set("sensor.dynamic_price", "0.35")

    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={
            **mock_config_entry.options,
            CONF_PRICE_MODE: PRICE_MODE_DYNAMIC,
            CONF_PRICE_SENSOR: "sensor.dynamic_price",
        },
    )

    result = await hass.config_entries.options.async_init(
        mock_config_entry.entry_id,
    )

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            "meter_value": 150.0,
            CONF_PRICE_MODE: PRICE_MODE_DYNAMIC,
            CONF_PRICE_SENSOR: "sensor.dynamic_price",
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY


async def test_options_flow_price_sensor_missing_device_class_still_selectable_via_yaml(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """A legacy price sensor without 'monetary' device_class still works as a default.

    The device_class filter only affects which entities are shown in the UI
    dropdown for new selections; an already-configured price_sensor continues
    to be used as the default regardless of its device_class, because the
    default is read directly from the config entry data/options.
    """
    hass.states.async_set("sensor.legacy_price", "0.35")

    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={
            **mock_config_entry.options,
            CONF_PRICE_SENSOR: "sensor.legacy_price",
        },
    )

    from custom_components.enerabot.options_flow import EnerABotOptionsFlow

    flow = EnerABotOptionsFlow(mock_config_entry)
    flow.hass = hass
    schema = flow.build_meter_correction_schema()

    schema_dict = schema.schema
    price_sensor_key = next(k for k in schema_dict if k == CONF_PRICE_SENSOR)
    assert price_sensor_key.default() == "sensor.legacy_price"  # type: ignore[attr-defined]
    # voluptuous stub gap: Optional is str subtype with .default

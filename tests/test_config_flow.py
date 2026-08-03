# tests/test_config_flow.py

"""Test the enerABot config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

import custom_components.enerabot.config_flow as config_flow
from custom_components.enerabot.const import (
    CONF_METER_ID,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    DOMAIN,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
)


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] is None or result["errors"] == {}


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    with patch(
        "custom_components.enerabot.config_flow.validate_input",
        side_effect=config_flow.CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "name": "Test Meter",
                "sensor": "sensor.nonexistent",
                "obis_code": "1.8.2",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_already_configured(hass: HomeAssistant) -> None:
    """Test we abort if already configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        unique_id="sensor.test_import",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    with patch(
        "custom_components.enerabot.config_flow.validate_input",
        return_value={
            "title": "Test Meter",
            "sensor": "sensor.test_import",
            "obis_code": "1.8.2",
        },
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "name": "Test Meter",
                "sensor": "sensor.test_import",
                "obis_code": "1.8.2",
            },
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_form_import_only(hass: HomeAssistant) -> None:
    """Test we can configure with an import sensor."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Import Only",
            "sensor": "sensor.test_import",
            "obis_code": "1.8.2",
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_SENSOR] == "sensor.test_import"
    assert result2["data"][CONF_OBIS_CODE] == "1.8.2"


async def test_form_export_only(hass: HomeAssistant) -> None:
    """Test we can configure with an export sensor."""
    hass.states.async_set("sensor.test_export", "50.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Export Only",
            "sensor": "sensor.test_export",
            "obis_code": "2.8.2",
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_SENSOR] == "sensor.test_export"
    assert result2["data"][CONF_OBIS_CODE] == "2.8.2"


async def test_form_no_sensor_configured_fails(hass: HomeAssistant) -> None:
    """Test we cannot proceed without a sensor configured."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test No Sensor",
            "sensor": "sensor.nonexistent",
            "obis_code": "1.8.2",
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_with_initial_meter_value_sets_offset(hass: HomeAssistant) -> None:
    """Test that providing initial reading calculates offset at setup."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Offset",
            "sensor": "sensor.test_import",
            "obis_code": "1.8.2",
            "initial_meter_value": 150.0,
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    options = result2["options"]
    assert options["offset"] == 50.0
    assert "last_correction" in options


async def test_form_without_initial_meter_value_no_offset(hass: HomeAssistant) -> None:
    """Test that no offset is set when initial meter value is not provided."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test No Initial",
            "sensor": "sensor.test_import",
            "obis_code": "1.8.2",
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    options = result2["options"]
    assert OPTION_OFFSET not in options
    assert OPTION_LAST_CORRECTION not in options


async def test_form_initial_meter_value_ignored_when_sensor_unavailable(
    hass: HomeAssistant,
) -> None:
    """Test that initial meter value is rejected when sensor is unavailable."""
    hass.states.async_set("sensor.test_import", "unavailable")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Unavailable",
            "sensor": "sensor.test_import",
            "obis_code": "1.8.2",
            "initial_meter_value": 150.0,
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] is not None
    assert result2["errors"]["base"] == "cannot_connect"


async def test_form_with_metadata_fields_saved(hass: HomeAssistant) -> None:
    """Test that OBIS code, meter ID and tariff price are persisted."""
    hass.states.async_set("sensor.test_import", "100.0")
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Metadata",
            "sensor": "sensor.test_import",
            "obis_code": "1.8.2",
            "meter_id": "1SAG1234567890",
            "tariff_price": 0.32,
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"]["meter_id"] == "1SAG1234567890"
    assert result2["data"]["obis_code"] == "1.8.2"
    assert result2["data"]["tariff_price"] == 0.32


async def test_form_metadata_fields_optional(hass: HomeAssistant) -> None:
    """Test that config succeeds without any metadata fields."""
    hass.states.async_set("sensor.test_import", "100.0")
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test No Metadata",
            "sensor": "sensor.test_import",
            "obis_code": "1.8.2",
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert "meter_id" not in result2["data"]


async def test_form_invalid_obis_code_fails(hass: HomeAssistant) -> None:
    """Test that a non-import/export OBIS code is rejected."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Invalid OBIS",
            "sensor": "sensor.test_import",
            "obis_code": "3.6.0",
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}

# tests/test_config_flow.py

"""Test the enerABot config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

import custom_components.enerabot.config_flow as config_flow
from custom_components.enerabot.const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    CONF_NAME,
    DOMAIN,
    OPTION_LAST_CORRECTION_IMPORT,
    OPTION_OFFSET_IMPORT,
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
                "import_sensor": "sensor.nonexistent",
                "export_sensor": "sensor.nonexistent2",
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
            CONF_IMPORT_SENSOR: "sensor.test_import",
            CONF_EXPORT_SENSOR: "sensor.test_export",
        },
        unique_id="sensor.test_import_sensor.test_export",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    with patch(
        "custom_components.enerabot.config_flow.validate_input",
        return_value={
            "title": "Test Meter",
            "import_sensor": "sensor.test_import",
            "export_sensor": "sensor.test_export",
        },
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "name": "Test Meter",
                "import_sensor": "sensor.test_import",
                "export_sensor": "sensor.test_export",
            },
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_form_import_only(hass: HomeAssistant) -> None:
    """Test we can configure with only an import sensor."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Import Only",
            "import_sensor": "sensor.test_import",
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_IMPORT_SENSOR] == "sensor.test_import"
    assert result2["data"].get(CONF_EXPORT_SENSOR) is None


async def test_form_export_only(hass: HomeAssistant) -> None:
    """Test we can configure with only an export sensor."""
    hass.states.async_set("sensor.test_export", "50.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Export Only",
            "export_sensor": "sensor.test_export",
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_EXPORT_SENSOR] == "sensor.test_export"
    assert result2["data"].get(CONF_IMPORT_SENSOR) is None


async def test_form_no_sensor_configured_fails(hass: HomeAssistant) -> None:
    """Test we cannot proceed without any sensor configured."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test No Sensor",
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_with_initial_import_meter_value_sets_offset(hass: HomeAssistant) -> None:
    """Test that providing initial import reading calculates offset at setup."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Offset",
            "import_sensor": "sensor.test_import",
            "initial_import_meter_value": 150.0,
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    options = result2["options"]
    assert options["offset_import"] == 50.0
    assert "last_correction_import" in options


async def test_form_without_initial_meter_value_no_offset(hass: HomeAssistant) -> None:
    """Test that no offset is set when initial meter value is not provided."""
    hass.states.async_set("sensor.test_import", "100.0")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test No Initial",
            "import_sensor": "sensor.test_import",
        },
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    options = result2["options"]
    assert OPTION_OFFSET_IMPORT not in options
    assert OPTION_LAST_CORRECTION_IMPORT not in options


async def test_form_initial_meter_value_ignored_when_sensor_unavailable(hass: HomeAssistant) -> None:
    """Test that initial meter value is rejected when sensor is unavailable."""
    hass.states.async_set("sensor.test_import", "unavailable")

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Test Unavailable",
            "import_sensor": "sensor.test_import",
            "initial_import_meter_value": 150.0,
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"]["base"] == "cannot_connect"

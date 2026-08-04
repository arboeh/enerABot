# tests/test_init.py

"""Tests for the enerABot __init__ module."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot import (
    async_migrate_entry,
    async_reload_entry,
    async_unload_entry,
    calculate_and_store_offset,
    reset_meter,
)
from custom_components.enerabot.const import (
    ATTR_RESET_ALL,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    DOMAIN,
    OPTION_COST_LAST_ENERGY,
    OPTION_COST_PERIOD_START,
    OPTION_COST_TOTAL,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
    SERVICE_RESET_METER,
)


@pytest.fixture
def mock_config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter",
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.0,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
        },
        unique_id="sensor.test_import",
    )
    entry.add_to_hass(hass)
    return entry


async def test_register_services(hass: HomeAssistant, setup_integration) -> None:
    """Test that the service registers and sets the offset."""
    with patch(
        "custom_components.enerabot.calculate_and_store_offset",
        new_callable=AsyncMock,
    ) as mock_calc:
        await hass.services.async_call(
            DOMAIN,
            "set_energy_meter",
            {
                "entity_id": "sensor.test_import",
                "meter_value": 1234.5,
            },
            blocking=True,
        )
        mock_calc.assert_called_once()
        call_args = mock_calc.call_args
        assert call_args[0][1] == "sensor.test_import"
        assert call_args[0][2] == 1234.5


async def test_calculate_and_store_offset_no_matching_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that a warning is logged when no matching config entry is found."""
    mock_config_entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})

    with patch("custom_components.enerabot.LOGGER.warning") as mock_warning:
        await calculate_and_store_offset(hass, "sensor.nonexistent", 1000.0)
        mock_warning.assert_called_once_with("No matching config entry found for entity %s", "sensor.nonexistent")


async def test_async_unload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that async_unload_entry removes the coordinator and deregisters services."""
    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    result = await async_unload_entry(hass, mock_config_entry)

    assert result is True
    assert mock_config_entry.entry_id not in hass.data.get(DOMAIN, {})


async def test_async_reload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test that async_reload_entry unloads and sets up the entry again."""
    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    with (
        patch.object(hass.config_entries, "async_unload_platforms", new=AsyncMock(return_value=True)),
        patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()),
        patch(
            "custom_components.enerabot.coordinator.EnerABotCoordinator.async_config_entry_first_refresh",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.enerabot.coordinator.EnerABotCoordinator.async_start_state_listener",
            new=AsyncMock(),
        ),
    ):
        await async_reload_entry(hass, mock_config_entry)

    assert mock_config_entry.entry_id in hass.data[DOMAIN]


async def test_migrate_entry_dual_sensor_splits_into_two(hass: HomeAssistant) -> None:
    """Test that a version 1 entry with both import and export sensors splits into two entries."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter",
        data={
            CONF_NAME: "Test Meter",
            "import_sensor": "sensor.test_import",
            "export_sensor": "sensor.test_export",
        },
        options={
            "offset_import": 0.5,
            "offset_export": 0.3,
            "last_correction_import": "2026-08-01T12:00:00+00:00",
            "last_correction_export": "2026-08-01T13:00:00+00:00",
        },
        version=1,
        unique_id="test_enerabot_meter",
    )
    entry.add_to_hass(hass)

    hass.states.async_set("sensor.test_import", "100.0")
    hass.states.async_set("sensor.test_export", "50.0")

    with patch(
        "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
        return_value=100.5,
    ):
        result = await async_migrate_entry(hass, entry)
        assert result is True

        await hass.async_block_till_done()

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 2

    import_entry = next(e for e in entries if e.data.get(CONF_SENSOR) == "sensor.test_import")
    export_entry = next(e for e in entries if e.data.get(CONF_SENSOR) == "sensor.test_export")

    assert import_entry.version == 2
    assert import_entry.data[CONF_OBIS_CODE] == "1.8.2"
    assert import_entry.options[OPTION_OFFSET] == 0.5
    assert import_entry.options[OPTION_LAST_CORRECTION] == "2026-08-01T12:00:00+00:00"

    assert export_entry.version == 2
    assert export_entry.data[CONF_OBIS_CODE] == "2.8.2"
    assert export_entry.data.get(CONF_NAME) == "Test Meter Export"


async def test_reset_meter_service_single(hass: HomeAssistant, setup_integration) -> None:
    """Test that reset_meter service resets a single matched meter."""
    entry = setup_integration

    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET_METER,
            {
                "entity_id": "sensor.test_import",
                ATTR_RESET_ALL: False,
            },
            blocking=True,
        )

        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][0] == entry
        new_options = call_args[1]["options"]
        assert new_options[OPTION_OFFSET] == 0.0
        assert new_options[OPTION_LAST_CORRECTION] is None
        assert new_options[OPTION_COST_TOTAL] == 0.0
        assert new_options[OPTION_COST_LAST_ENERGY] is None
        assert new_options[OPTION_COST_PERIOD_START] is None


async def test_reset_meter_service_all(hass: HomeAssistant, setup_integration) -> None:
    """Test that reset_meter with reset_all resets every configured meter."""
    entry = setup_integration

    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET_METER,
            {ATTR_RESET_ALL: True},
            blocking=True,
        )

        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][0] == entry
        new_options = call_args[1]["options"]
        assert new_options[OPTION_OFFSET] == 0.0
        assert new_options[OPTION_LAST_CORRECTION] is None


async def test_reset_meter_no_matching_entity(hass: HomeAssistant, setup_integration) -> None:
    """Test that reset_meter with a non-matching entity_id does nothing."""
    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        await reset_meter(hass, "sensor.nonexistent", reset_all=False)
        mock_update.assert_not_called()


async def test_reset_meter_function_preserves_other_options(hass: HomeAssistant) -> None:
    """Test that reset_meter preserves options that are not being reset."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter",
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.5,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
            CONF_TARIFF_PRICE: 0.32,
        },
        unique_id="sensor.test_import_preserves",
    )
    entry.add_to_hass(hass)

    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        await reset_meter(hass, "sensor.test_import", reset_all=False)
        mock_update.assert_called_once()
        new_options = mock_update.call_args[1]["options"]
        assert new_options[OPTION_OFFSET] == 0.0
        assert new_options[OPTION_COST_TOTAL] == 0.0
        assert new_options.get(CONF_TARIFF_PRICE) == 0.32


async def test_reset_meter_service_resets_single_entry(hass: HomeAssistant, setup_integration) -> None:
    """reset_meter with entity_id should only reset the matching entry."""
    entry = setup_integration

    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET_METER,
            {
                "entity_id": "sensor.test_import",
                ATTR_RESET_ALL: False,
            },
            blocking=True,
        )

        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][0] == entry
        new_options = call_args[1]["options"]
        assert new_options[OPTION_OFFSET] == 0.0
        assert new_options[OPTION_LAST_CORRECTION] is None
        assert new_options[OPTION_COST_TOTAL] == 0.0
        assert new_options[OPTION_COST_LAST_ENERGY] is None
        assert new_options[OPTION_COST_PERIOD_START] is None


async def test_reset_meter_service_reset_all(hass: HomeAssistant) -> None:
    """reset_meter with reset_all=true should reset every configured entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter",
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.5,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
            CONF_TARIFF_PRICE: 0.32,
        },
        unique_id="sensor.test_import_reset_all",
    )
    entry.add_to_hass(hass)

    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        await reset_meter(hass, reset_all=True)

        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][0] == entry
        new_options = call_args[1]["options"]
        assert new_options[OPTION_OFFSET] == 0.0
        assert new_options[OPTION_LAST_CORRECTION] is None
        assert new_options[OPTION_COST_TOTAL] == 0.0
        assert new_options[OPTION_COST_LAST_ENERGY] is None
        assert new_options[OPTION_COST_PERIOD_START] is None
        assert new_options.get(CONF_TARIFF_PRICE) == 0.32


async def test_reset_meter_service_no_matching_entry_logs_warning(hass: HomeAssistant, setup_integration) -> None:
    """Should log a warning if entity_id matches no config entry."""
    with patch("custom_components.enerabot.LOGGER.warning") as mock_warning:
        await reset_meter(hass, "sensor.nonexistent", reset_all=False)

        mock_warning.assert_called_once_with("No matching config entry found for entity %s", "sensor.nonexistent")


async def test_reset_meter_button_entity(hass: HomeAssistant, setup_integration) -> None:
    """Test that the reset button entity is created."""
    from homeassistant.helpers import entity_registry as er

    entry = setup_integration
    entity_registry = er.async_get(hass)
    button_entity_id = entity_registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_reset")
    assert button_entity_id is not None


async def test_reset_meter_button_press(hass: HomeAssistant, setup_integration) -> None:
    """Test that pressing the reset button triggers async_update_entry."""
    from homeassistant.helpers import entity_registry as er

    entry = setup_integration
    entity_registry = er.async_get(hass)
    button_entity_id = entity_registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_reset")
    assert button_entity_id is not None

    with patch.object(hass.config_entries, "async_update_entry") as mock_update:
        await hass.services.async_call("button", "press", {"entity_id": button_entity_id}, blocking=True)
        await hass.async_block_till_done()

        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][0] == entry
        new_options = call_args[1]["options"]
        assert new_options[OPTION_OFFSET] == 0.0
        assert new_options[OPTION_LAST_CORRECTION] is None
        assert new_options[OPTION_COST_TOTAL] == 0.0

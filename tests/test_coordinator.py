# tests/test_coordinator.py

"""Test the enerABot coordinator."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_COST_RESET_CYCLE,
    CONF_NAME,
    CONF_OBIS_CODE,
    CONF_PRICE_MODE,
    CONF_PRICE_SENSOR,
    CONF_SENSOR,
    CONF_TARIFF_PRICE,
    COST_RESET_MONTHLY,
    COST_RESET_NONE,
    COST_RESET_YEARLY,
    DOMAIN,
    OPTION_COST_LAST_ENERGY,
    OPTION_COST_PERIOD_START,
    OPTION_COST_TOTAL,
    PRICE_MODE_DYNAMIC,
    PRICE_MODE_FIXED,
    PRICE_MODE_NONE,
)
from custom_components.enerabot.coordinator import EnerABotCoordinator


@pytest.fixture
def mock_config_entry(hass):
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
            "offset": 1.5,
        },
        unique_id="sensor.test_import",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_config_entry_export_only(hass):
    """Create a mock config entry with only an export sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Export Only",
        data={
            CONF_NAME: "Test Export Only",
            CONF_SENSOR: "sensor.test_export",
            CONF_OBIS_CODE: "2.8.2",
        },
        options={
            "offset": 0.5,
        },
        unique_id="sensor.test_export",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_config_entry_import_only(hass):
    """Create a mock config entry with only an import sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Import Only",
        data={
            CONF_NAME: "Test Import Only",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            "offset": 1.5,
        },
        unique_id="sensor.test_import_only",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_coordinator(hass, mock_config_entry):
    """Create a coordinator."""
    coordinator = EnerABotCoordinator(hass, mock_config_entry)
    return coordinator


@pytest.fixture
def mock_coordinator_export_only(hass, mock_config_entry_export_only):
    """Create a coordinator with only an export sensor."""
    coordinator = EnerABotCoordinator(hass, mock_config_entry_export_only)
    return coordinator


async def test_coordinator_update_data(hass: HomeAssistant, mock_coordinator):
    """Test coordinator data update with offset applied."""
    hass.states.async_set("sensor.test_import", "100.0")

    data = await mock_coordinator._async_update_data()

    assert data == 101.5


async def test_coordinator_update_data_no_offset(hass: HomeAssistant, mock_config_entry, mock_coordinator):
    """Test coordinator data update without offset."""
    hass.config_entries.async_update_entry(mock_config_entry, options={})
    await hass.async_block_till_done()

    hass.states.async_set("sensor.test_import", "100.0")

    data = await mock_coordinator._async_update_data()

    assert data == 100.0


async def test_coordinator_update_data_unavailable(hass: HomeAssistant, mock_coordinator):
    """Test coordinator handles unavailable sensor gracefully."""
    hass.states.async_set("sensor.test_import", "unavailable")

    data = await mock_coordinator._async_update_data()

    assert data is None


async def test_coordinator_update_data_unknown(hass: HomeAssistant, mock_coordinator):
    """Test coordinator handles unknown sensor gracefully."""
    hass.states.async_set("sensor.test_import", "unknown")

    data = await mock_coordinator._async_update_data()

    assert data is None


async def test_coordinator_export_only(hass: HomeAssistant, mock_coordinator_export_only):
    """Test coordinator with only an export sensor configured."""
    hass.states.async_set("sensor.test_export", "100.0")

    data = await mock_coordinator_export_only._async_update_data()

    assert data == 100.5


@pytest.fixture
def mock_price_sensor_entry(hass):
    """Create a config entry with a dynamic price sensor."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Price Sensor",
        data={
            CONF_NAME: "Test Price Sensor",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
            CONF_PRICE_MODE: PRICE_MODE_DYNAMIC,
            CONF_PRICE_SENSOR: "sensor.dynamic_price",
        },
        options={
            CONF_PRICE_MODE: PRICE_MODE_DYNAMIC,
            CONF_PRICE_SENSOR: "sensor.dynamic_price",
        },
        unique_id="sensor.test_price_sensor",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_fixed_price_entry(hass):
    """Create a config entry with a fixed price."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Fixed Price",
        data={
            CONF_NAME: "Test Fixed Price",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_TARIFF_PRICE: 0.35,
        },
        options={
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_TARIFF_PRICE: 0.35,
            CONF_COST_RESET_CYCLE: COST_RESET_NONE,
        },
        unique_id="sensor.test_fixed_price",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_fixed_price_monthly_entry(hass):
    """Create a config entry with a fixed price and monthly reset cycle."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Fixed Price Monthly",
        data={
            CONF_NAME: "Test Fixed Price Monthly",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_TARIFF_PRICE: 0.35,
        },
        options={
            CONF_PRICE_MODE: PRICE_MODE_FIXED,
            CONF_TARIFF_PRICE: 0.35,
            CONF_COST_RESET_CYCLE: COST_RESET_MONTHLY,
        },
        unique_id="sensor.test_fixed_price_monthly",
    )
    entry.add_to_hass(hass)
    return entry


async def test_get_current_price_none_mode(hass: HomeAssistant, mock_config_entry):
    """Test _get_current_price returns None when price_mode is none."""
    coordinator = EnerABotCoordinator(hass, mock_config_entry)
    assert coordinator._get_current_price() is None


async def test_get_current_price_fixed(hass: HomeAssistant, mock_fixed_price_entry):
    """Test _get_current_price returns tariff_price when price_mode is fixed."""
    coordinator = EnerABotCoordinator(hass, mock_fixed_price_entry)
    assert coordinator._get_current_price() == 0.35


async def test_get_current_price_dynamic(hass: HomeAssistant, mock_price_sensor_entry):
    """Test _get_current_price returns sensor state when price_mode is dynamic."""
    hass.states.async_set("sensor.dynamic_price", "0.28")
    coordinator = EnerABotCoordinator(hass, mock_price_sensor_entry)
    assert coordinator._get_current_price() == 0.28


async def test_get_current_price_dynamic_unavailable(hass: HomeAssistant, mock_price_sensor_entry):
    """Test _get_current_price returns None when dynamic price sensor is unavailable."""
    hass.states.async_set("sensor.dynamic_price", "unavailable")
    coordinator = EnerABotCoordinator(hass, mock_price_sensor_entry)
    assert coordinator._get_current_price() is None


async def test_get_current_price_dynamic_non_numeric(hass: HomeAssistant, mock_price_sensor_entry):
    """Test _get_current_price returns None when dynamic price sensor is non-numeric."""
    hass.states.async_set("sensor.dynamic_price", "abc")
    coordinator = EnerABotCoordinator(hass, mock_price_sensor_entry)
    assert coordinator._get_current_price() is None


async def test_coordinator_calculate_offset_value(hass: HomeAssistant, mock_coordinator):
    """Test _calculate_offset_value returns the offset-corrected value."""
    hass.states.async_set("sensor.test_import", "100.0")
    assert mock_coordinator._calculate_offset_value() == 101.5


async def test_coordinator_calculate_offset_value_unavailable(hass: HomeAssistant, mock_coordinator):
    """Test _calculate_offset_value returns None when sensor is unavailable."""
    hass.states.async_set("sensor.test_import", "unavailable")
    assert mock_coordinator._calculate_offset_value() is None


async def test_update_cost_no_tariff_price(hass: HomeAssistant, mock_coordinator):
    """Test _update_cost early-returns when no tariff_price is configured."""
    hass.states.async_set("sensor.test_import", "100.0")
    await mock_coordinator._update_cost(100.0)
    assert mock_coordinator.cost_total is None


async def test_update_cost_accumulates(hass: HomeAssistant, mock_fixed_price_entry):
    """Test that cost accumulates incrementally."""
    coordinator = EnerABotCoordinator(hass, mock_fixed_price_entry)
    hass.states.async_set("sensor.test_import", "100.0")

    await coordinator._update_cost(100.0)
    assert coordinator.cost_total == 0.0

    await coordinator._update_cost(101.0)
    expected = round(0.0 + (101.0 - 100.0) * 0.35, 2)
    assert coordinator.cost_total == expected


async def test_update_cost_first_call_initializes(hass: HomeAssistant, mock_fixed_price_entry):
    """Test that first call initializes period_start and last_energy."""
    coordinator = EnerABotCoordinator(hass, mock_fixed_price_entry)
    await coordinator._update_cost(50.0)

    assert coordinator._cost_period_start is not None
    assert coordinator._cost_last_energy == 50.0
    assert coordinator._cost_total == 0.0


async def test_update_cost_reset_monthly(hass: HomeAssistant, mock_fixed_price_monthly_entry):
    """Test that cost resets when the month changes."""
    from datetime import UTC, datetime

    coordinator = EnerABotCoordinator(hass, mock_fixed_price_monthly_entry)
    coordinator._cost_period_start = (datetime.now(UTC).replace(month=1, day=1)).isoformat()
    coordinator._cost_total = 100.0
    coordinator._cost_last_energy = 50.0

    # Simulate a state change in a different month
    new_period = datetime.now(UTC).replace(month=6, day=15)
    with patch("custom_components.enerabot.coordinator.datetime") as mock_dt:
        mock_dt.now.return_value = new_period
        mock_dt.fromisoformat = datetime.fromisoformat
        mock_dt.side_effect = lambda *a, **kw: new_period
        await coordinator._update_cost(51.0)

    assert coordinator.cost_total == 0.0
    assert coordinator._cost_last_energy == 51.0


async def test_update_cost_no_reset_when_cycle_none(hass: HomeAssistant, mock_fixed_price_entry):
    """Test that cost does not reset when cost_reset_cycle is none."""
    coordinator = EnerABotCoordinator(hass, mock_fixed_price_entry)
    coordinator._cost_period_start = "2026-01-01T00:00:00+00:00"
    coordinator._cost_total = 50.0
    coordinator._cost_last_energy = 100.0

    await coordinator._update_cost(101.0)
    expected = round(50.0 + (101.0 - 100.0) * 0.35, 2)
    assert coordinator.cost_total == expected


async def test_state_listener_tracks_price_sensor(hass: HomeAssistant, mock_price_sensor_entry):
    """Test that the state listener also tracks the price sensor entity."""
    coordinator = EnerABotCoordinator(hass, mock_price_sensor_entry)
    await coordinator.async_start_state_listener()

    assert coordinator.unsub_state_changes is not None
    await coordinator.async_shutdown()


async def test_coordinator_cost_accumulates_with_price(hass: HomeAssistant, mock_config_entry):
    """Cost should increase proportionally to energy delta and price."""
    hass.config_entries.async_update_entry(
        mock_config_entry,
        options={**mock_config_entry.options, CONF_PRICE_MODE: PRICE_MODE_FIXED, CONF_TARIFF_PRICE: 0.30},
    )
    coordinator = EnerABotCoordinator(hass, mock_config_entry)
    hass.states.async_set("sensor.test_import", "100.0")
    await coordinator._async_update_data()
    hass.states.async_set("sensor.test_import", "110.0")
    await coordinator._async_update_data()
    assert coordinator.cost_total == pytest.approx(3.0)


async def test_coordinator_cost_resets_monthly(hass: HomeAssistant, mock_fixed_price_monthly_entry, freezer):
    """Cost total should reset to 0 when the month changes."""
    from datetime import UTC, datetime

    freezer.move_to(datetime(2026, 1, 31, 23, 0, 0, tzinfo=UTC))
    coordinator = EnerABotCoordinator(hass, mock_fixed_price_monthly_entry)
    hass.states.async_set("sensor.test_import", "100.0")
    await coordinator._async_update_data()
    assert coordinator.cost_total == 0.0

    hass.states.async_set("sensor.test_import", "105.0")
    await coordinator._async_update_data()
    assert coordinator.cost_total == pytest.approx(1.75)

    freezer.move_to(datetime(2026, 2, 1, 0, 0, 0, tzinfo=UTC))
    hass.states.async_set("sensor.test_import", "108.0")
    await coordinator._async_update_data()
    assert coordinator.cost_total == 0.0


async def test_coordinator_cost_none_cycle_never_resets(hass: HomeAssistant, mock_fixed_price_entry, freezer):
    """cost_reset_cycle=none should never reset accumulated cost."""
    from datetime import UTC, datetime

    freezer.move_to(datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC))
    coordinator = EnerABotCoordinator(hass, mock_fixed_price_entry)
    hass.states.async_set("sensor.test_import", "100.0")
    await coordinator._async_update_data()

    hass.states.async_set("sensor.test_import", "110.0")
    await coordinator._async_update_data()
    first_cost = coordinator.cost_total
    assert first_cost is not None
    assert first_cost == pytest.approx(3.5)

    freezer.move_to(datetime(2026, 2, 15, 12, 0, 0, tzinfo=UTC))
    hass.states.async_set("sensor.test_import", "120.0")
    await coordinator._async_update_data()
    expected = first_cost + (120.0 - 110.0) * 0.35
    assert coordinator.cost_total == pytest.approx(expected)


async def test_coordinator_no_cost_without_tariff_price(hass: HomeAssistant, mock_config_entry):
    """No cost tracking should occur when tariff_price is not configured."""
    coordinator = EnerABotCoordinator(hass, mock_config_entry)
    hass.states.async_set("sensor.test_import", "100.0")
    await coordinator._async_update_data()
    assert coordinator.cost_total is None


async def test_update_cost_accumulates_with_dynamic_price(hass: HomeAssistant, mock_price_sensor_entry):
    """Cost should accumulate using the dynamic price sensor, not tariff_price."""
    hass.states.async_set("sensor.dynamic_price", "0.40")
    coordinator = EnerABotCoordinator(hass, mock_price_sensor_entry)
    hass.states.async_set("sensor.test_import", "100.0")
    await coordinator._update_cost(100.0)
    await coordinator._update_cost(102.0)
    assert coordinator.cost_total == pytest.approx(0.80)

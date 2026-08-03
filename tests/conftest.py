# tests/conftest.py

"""Fixtures for enerABot tests."""

import logging
import uuid
import warnings
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    CONF_NAME,
    DOMAIN,
)

logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("homeassistant").setLevel(logging.WARNING)
logging.getLogger("custom_components.enerabot").setLevel(logging.INFO)

warnings.filterwarnings("ignore", message=".*custom integration.*has not been tested.*")

logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("homeassistant").setLevel(logging.ERROR)
logging.getLogger("pytest_homeassistant_custom_component").setLevel(logging.ERROR)
logging.getLogger("custom_components.enerabot").setLevel(logging.INFO)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Automatically enable custom integrations."""
    yield


@pytest.fixture
def mock_config_entry(hass: HomeAssistant):
    """Create a mock config entry."""
    unique_id = str(uuid.uuid4())
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Meter Pair",
        data={
            CONF_NAME: "Test Meter",
            CONF_IMPORT_SENSOR: "sensor.test_import",
            CONF_EXPORT_SENSOR: "sensor.test_export",
        },
        options={
            "offset_import": 0.0,
            "offset_export": 0.0,
        },
        unique_id=f"sensor.test_import_sensor.test_export",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_config_entry):
    """Set up the enerABot integration."""
    with (
        patch(
            "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
            return_value={
                "import_value": 100.5,
                "export_value": 50.2,
            },
        ),
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state == ConfigEntryState.LOADED

        yield mock_config_entry

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

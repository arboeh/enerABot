# tests/conftest.py

"""Fixtures for enerABot tests."""

import logging
import sys
import uuid
import warnings
from unittest.mock import AsyncMock, patch

import pytest
import pytest_socket
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enerabot.const import (
    CONF_EXPORT_SENSOR,
    CONF_IMPORT_SENSOR,
    CONF_NAME,
    DOMAIN,
    OPTION_LAST_CORRECTION_EXPORT,
    OPTION_LAST_CORRECTION_IMPORT,
    OPTION_OFFSET_EXPORT,
    OPTION_OFFSET_IMPORT,
)

if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session", autouse=True)
def event_loop_policy():
    """Force SelectorEventLoop policy for the entire test session on Windows."""
    if sys.platform == "win32":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.get_event_loop_policy()


pytest_socket.disable_socket = lambda *args, **kwargs: None
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
            OPTION_OFFSET_IMPORT: 0.0,
            OPTION_OFFSET_EXPORT: 0.0,
            OPTION_LAST_CORRECTION_IMPORT: "2026-08-01T12:00:00+00:00",
            OPTION_LAST_CORRECTION_EXPORT: "2026-08-01T12:00:00+00:00",
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

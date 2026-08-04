# tests/conftest.py

"""Fixtures for enerABot tests."""

import asyncio
import logging
import sys
import uuid
import warnings
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

if sys.platform == "win32":
    import types

    if sys.modules.get("fcntl") is None:
        _fcntl_stub: Any = types.ModuleType("fcntl")
        _fcntl_stub.LOCK_EX = 1
        _fcntl_stub.LOCK_NB = 2
        _fcntl_stub.LOCK_SH = 4
        _fcntl_stub.LOCK_UN = 8
        _fcntl_stub.flock = lambda *args, **kwargs: None
        sys.modules["fcntl"] = _fcntl_stub

    if sys.modules.get("resource") is None:
        _resource_stub: Any = types.ModuleType("resource")
        _resource_stub.RLIMIT_NOFILE = 7
        _resource_stub.getrlimit = lambda *a, **kw: (256, 4096)
        _resource_stub.setrlimit = lambda *a, **kw: None
        sys.modules["resource"] = _resource_stub

import pytest_socket
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

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

if sys.platform == "win32":
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
        title="Test Meter",
        data={
            CONF_NAME: "Test Meter",
            CONF_SENSOR: "sensor.test_import",
            CONF_OBIS_CODE: "1.8.2",
        },
        options={
            OPTION_OFFSET: 0.5,
            OPTION_LAST_CORRECTION: "2026-08-01T12:00:00+00:00",
            CONF_METER_ID: "1SAG1234567890",
            CONF_TARIFF_PRICE: 0.32,
        },
        unique_id="sensor.test_import",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_config_entry):
    """Set up the enerABot integration."""
    with (
        patch(
            "custom_components.enerabot.coordinator.EnerABotCoordinator._async_update_data",
            return_value=100.5,
        ),
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state == ConfigEntryState.LOADED

        yield mock_config_entry

    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

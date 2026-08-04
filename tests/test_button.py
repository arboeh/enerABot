# tests/test_button.py

"""Test the enerABot reset button entity."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.enerabot.const import (
    CONF_TARIFF_PRICE,
    DOMAIN,
    OPTION_COST_LAST_ENERGY,
    OPTION_COST_PERIOD_START,
    OPTION_COST_TOTAL,
    OPTION_LAST_CORRECTION,
    OPTION_OFFSET,
)


async def test_reset_button_created(hass: HomeAssistant, setup_integration) -> None:
    """Test that the reset button entity is created."""
    entry = setup_integration
    entity_registry = er.async_get(hass)
    button_entity_id = entity_registry.async_get_entity_id("button", DOMAIN, f"{entry.entry_id}_reset")
    assert button_entity_id is not None

    state = hass.states.get(button_entity_id)
    assert state is not None
    assert state.name == "Test Meter Reset"


async def test_reset_button_press_resets_offset_and_cost(hass: HomeAssistant, setup_integration) -> None:
    """Test that pressing the button resets offset and cost to defaults."""
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
        assert new_options[OPTION_COST_LAST_ENERGY] is None
        assert new_options[OPTION_COST_PERIOD_START] is None
        assert new_options[CONF_TARIFF_PRICE] == 0.32

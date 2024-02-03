"""Valetudo Quirks custom_component for Home Assistant."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Forward the setup to the select platform.
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "select")
    )
    return True

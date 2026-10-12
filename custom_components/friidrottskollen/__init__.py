"""Friidrottskollen – när och var en svensk friidrottare tävlar."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import FriidrottskollenCoordinator

PLATFORMS = [Platform.SENSOR, Platform.CALENDAR]

type FriidrottskollenConfigEntry = ConfigEntry[FriidrottskollenCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: FriidrottskollenConfigEntry) -> bool:
    coordinator = FriidrottskollenCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FriidrottskollenConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

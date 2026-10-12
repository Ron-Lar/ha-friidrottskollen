"""Sensorer: nästa tävling och nästa tävlingsdag."""
from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import FriidrottskollenConfigEntry
from .entity import FriidrottskollenEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: FriidrottskollenConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    c = entry.runtime_data
    async_add_entities([NastaTavling(c, "nasta"), NastaTavlingsdag(c, "nasta_datum")])


class NastaTavling(FriidrottskollenEntity, SensorEntity):
    _attr_name = "Nästa tävling"
    _attr_icon = "mdi:podium"

    @property
    def native_value(self) -> str:
        k = self.coordinator.kommande
        return k[0]["namn"][:255] if k else "Ingen planerad"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"tavlingar": self.coordinator.kommande, "uppdaterad": self.coordinator.uppdaterad}


class NastaTavlingsdag(FriidrottskollenEntity, SensorEntity):
    _attr_name = "Nästa tävlingsdag"
    _attr_device_class = SensorDeviceClass.DATE
    _attr_icon = "mdi:calendar-star"

    @property
    def native_value(self) -> date | None:
        k = self.coordinator.kommande
        return date.fromisoformat(k[0]["datum"]) if k else None

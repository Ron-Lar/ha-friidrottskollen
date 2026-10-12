"""Gemensam basklass."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KOLLEN_URL
from .coordinator import FriidrottskollenCoordinator


class FriidrottskollenEntity(CoordinatorEntity[FriidrottskollenCoordinator]):
    _attr_has_entity_name = True
    _attr_attribution = "Data från Svenska Friidrottsförbundet, friidrott.se"

    def __init__(self, coordinator: FriidrottskollenCoordinator, nyckel: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{nyckel}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.atlet,
            manufacturer="Friidrottskollen",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=KOLLEN_URL,
        )

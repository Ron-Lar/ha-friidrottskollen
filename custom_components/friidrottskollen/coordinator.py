"""Hämtar data från friidrott.se."""
from __future__ import annotations

import asyncio
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import CONF_ATHLETE, DOMAIN, HEADERS, KOLLEN_URL, SCAN_INTERVAL, TV_URL
from .parser import match_tv, parse_kollen, parse_tv

_LOGGER = logging.getLogger(__name__)


async def hamta(hass: HomeAssistant, url: str) -> str:
    session = async_get_clientsession(hass)
    async with asyncio.timeout(30):
        resp = await session.get(url, headers=HEADERS)
        resp.raise_for_status()
        return await resp.text()


class FriidrottskollenCoordinator(DataUpdateCoordinator[list[dict]]):
    """Alla tävlingar för en idrottare, med TV-uppgifter."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {entry.data[CONF_ATHLETE]}",
            update_interval=SCAN_INTERVAL,
            config_entry=entry,
        )
        self.atlet: str = entry.data[CONF_ATHLETE]
        self.uppdaterad: str | None = None

    async def _async_update_data(self) -> list[dict]:
        try:
            kollen_html = await hamta(self.hass, KOLLEN_URL)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Kunde inte hämta Friidrottskollen: {err}") from err

        tavlingar = await self.hass.async_add_executor_job(parse_kollen, kollen_html, self.atlet)

        try:
            tv_html = await hamta(self.hass, TV_URL)
            rader = await self.hass.async_add_executor_job(parse_tv, tv_html)
            match_tv(tavlingar, rader)
        except (aiohttp.ClientError, TimeoutError) as err:
            # TV är en bonus – tävlingarna visas ändå
            _LOGGER.warning("Kunde inte hämta TV-tablån: %s", err)

        self.uppdaterad = dt_util.utcnow().isoformat()
        return tavlingar

    @property
    def kommande(self) -> list[dict]:
        idag = dt_util.now().date().isoformat()
        return [t for t in (self.data or []) if t["slut"] >= idag]

"""Kalender med alla tävlingar."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import FriidrottskollenConfigEntry
from .entity import FriidrottskollenEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: FriidrottskollenConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([Tavlingskalender(entry.runtime_data, "kalender")])


def _beskrivning(t: dict) -> str | None:
    rader = []
    if t.get("tv"):
        rader.append(f"TV: {t['tv']}" + (f" {t['tid']}" if t.get("tid") else ""))
    if t.get("tvLank"):
        rader.append(f"Sändning: {t['tvLank']}")
    if t.get("lank"):
        rader.append(f"Tävlingens hemsida: {t['lank']}")
    return "\n".join(rader) or None


class Tavlingskalender(FriidrottskollenEntity, CalendarEntity):
    _attr_name = "Tävlingar"
    _attr_icon = "mdi:calendar-star"

    def _handelser(self) -> list[CalendarEvent]:
        return [
            CalendarEvent(
                summary=t["namn"],
                start=date.fromisoformat(t["datum"]),
                end=date.fromisoformat(t["slut"]) + timedelta(days=1),  # heldag: slut är exklusivt
                location=t.get("plats"),
                description=_beskrivning(t),
            )
            for t in (self.coordinator.data or [])
        ]

    @property
    def event(self) -> CalendarEvent | None:
        idag = dt_util.now().date()
        return next((e for e in self._handelser() if e.end > idag), None)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        s, e = start_date.date(), end_date.date()
        return [h for h in self._handelser() if h.start <= e and h.end > s]

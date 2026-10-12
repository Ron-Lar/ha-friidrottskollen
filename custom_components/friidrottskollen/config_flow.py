"""Konfiguration via UI."""
from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.util import slugify

from .const import CONF_ATHLETE, DEFAULT_ATHLETE, DOMAIN, KOLLEN_URL
from .coordinator import hamta


class FriidrottskollenConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            atlet = " ".join(user_input[CONF_ATHLETE].split())
            await self.async_set_unique_id(slugify(atlet))
            self._abort_if_unique_id_configured()
            try:
                await hamta(self.hass, KOLLEN_URL)
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=atlet, data={CONF_ATHLETE: atlet})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ATHLETE, default=DEFAULT_ATHLETE): str}),
            errors=errors,
        )

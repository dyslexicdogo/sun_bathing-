"""Config flow for Sun Bathing — placeholder, one step, no fields yet."""

from __future__ import annotations

from homeassistant import config_entries

from .const import DOMAIN


class SunBathingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sun Bathing."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """First and only step — just create the entry to prove wiring."""
        if user_input is not None:
            return self.async_create_entry(title="Sun Bathing", data={})

        return self.async_show_form(step_id="user")
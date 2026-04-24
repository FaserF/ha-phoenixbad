"""Config flow for Phönix-Bad Ottobrunn."""
from __future__ import annotations

import homeassistant.helpers.config_validation as cv
from homeassistant import config_entries

from .const import DOMAIN

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


class PhoenixBadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    """Handle a config flow for Phönix Bad."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(title="Phönix Bad", data={})

        return self.async_show_form(step_id="user")

    async def async_step_import(self, user_input=None):
        """Handle the import step."""
        return await self.async_step_user(user_input)

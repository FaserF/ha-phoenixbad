from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN

class PhoenixBadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Phönix Bad."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        existing_entries = self.hass.config_entries.async_entries(DOMAIN)
        if existing_entries:
            return self.async_abort(reason="already_configured")

        return self.async_create_entry(title="Phönix Bad", data={})

    async def async_step_import(self, user_input=None):
        """Handle the import step."""
        return self.async_create_entry(title="Phönix Bad", data={})

    async def async_abort(self, reason):
        """Handle the abort of the config flow."""
        if reason == "already_configured":
            return self.async_abort(reason=reason)
        return await super().async_abort(reason)

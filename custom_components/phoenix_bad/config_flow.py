from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN

class PhoenixBadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Phönix Bad."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Here we directly create the entry without any user input
        return self.async_create_entry(title="Phönix Bad", data={})

    async def async_step_import(self, user_input=None):
        """Handle the import step."""
        return self.async_create_entry(title="Phönix Bad", data={})

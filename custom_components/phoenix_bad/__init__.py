from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up Phönix-Bad integration."""
    _LOGGER.debug("Phönix-Bad integration setup called.")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Phönix-Bad from a config entry."""
    _LOGGER.debug("Setting up Phönix-Bad entry with entry_id: %s", entry.entry_id)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    hass.data[DOMAIN] = {}
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Phönix-Bad config entry."""
    _LOGGER.debug("Unloading Phönix-Bad entry with entry_id: %s", entry.entry_id)
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True

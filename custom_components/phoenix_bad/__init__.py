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

    from .coordinator import PhoenixBadCoordinator
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    session = async_get_clientsession(hass)
    coordinator = PhoenixBadCoordinator(hass, session)

    # Initial fetch
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Phönix-Bad config entry."""
    _LOGGER.debug("Unloading Phönix-Bad entry with entry_id: %s", entry.entry_id)
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

"""Phoenix-Bad Ottobrunn integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS
from .coordinator import PhoenixBadCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):  # pylint: disable=unused-argument
    """Set up Phönix-Bad integration."""
    _LOGGER.debug("Phönix-Bad integration setup called.")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Phönix-Bad from a config entry."""
    _LOGGER.debug("Setting up Phönix-Bad entry with entry_id: %s", entry.entry_id)

    session = async_get_clientsession(hass)
    coordinator = PhoenixBadCoordinator(hass, session)

    # Initial fetch
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload Phönix-Bad config entry."""
    _LOGGER.debug("Unloading Phönix-Bad entry with entry_id: %s", entry.entry_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

"""Diagnostics support for Phoenix-Bad."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.diagnostics import async_redact_data

from .const import DOMAIN
from .coordinator import PhoenixBadCoordinator

TO_REDACT = {
    "entry_id",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PhoenixBadCoordinator = hass.data[DOMAIN][entry.entry_id]

    diagnostics_data = {
        "config_entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "coordinator_data": {},
    }

    if coordinator.data:
        for area, data in coordinator.data.items():
            diagnostics_data["coordinator_data"][area] = {
                "free": data.free,
                "occupied": data.occupied,
                "percentage": data.percentage,
                "total": data.total,
            }

    return diagnostics_data

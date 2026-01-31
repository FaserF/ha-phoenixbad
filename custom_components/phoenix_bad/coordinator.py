"""DataUpdateCoordinator for Phoenix-Bad."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp

from .api import PhoenixBadApiClient, PhoenixBadApiError, OccupancyData
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PhoenixBadCoordinator(DataUpdateCoordinator[dict[str, OccupancyData]]):
    """Class to manage fetching Phoenix-Bad data."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        scan_interval: timedelta | None = None,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            session: aiohttp session to use
            scan_interval: Update interval (defaults to DEFAULT_SCAN_INTERVAL)
        """
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval or DEFAULT_SCAN_INTERVAL,
        )
        self.api = PhoenixBadApiClient(session=session)

    async def _async_update_data(self) -> dict[str, OccupancyData]:
        """Fetch data from API.

        Returns:
            Dictionary with 'pool' and 'sauna' keys containing OccupancyData

        Raises:
            UpdateFailed: If update fails
        """
        try:
            _LOGGER.debug("Fetching Phoenix-Bad occupancy data")
            data = await self.api.get_all_occupancy()
            _LOGGER.debug("Successfully fetched data for %d areas", len(data))
            return data
        except PhoenixBadApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

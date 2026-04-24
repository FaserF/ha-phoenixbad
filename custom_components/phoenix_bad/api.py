"""API client for Phoenix-Bad Ottobrunn."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

# API endpoints
POOL_URL = (
    "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateLiveVisitors&area=Bad"
)
SAUNA_URL = (
    "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateLiveVisitors&area=Sauna"
)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

DEFAULT_TIMEOUT = 20


class PhoenixBadApiError(Exception):
    """Base exception for Phoenix-Bad API errors."""


class PhoenixBadConnectionError(PhoenixBadApiError):
    """Exception raised when connection to API fails."""


class PhoenixBadParseError(PhoenixBadApiError):
    """Exception raised when parsing API response fails."""


class OccupancyData:
    """Represents occupancy data for an area."""

    def __init__(self, free: int, occupied: int, percentage: float) -> None:
        """Initialize occupancy data.

        Args:
            free: Number of free spaces
            occupied: Number of occupied spaces
            percentage: Occupancy percentage (0-100)
        """
        self.free = free
        self.occupied = occupied
        self.percentage = percentage
        self.total = free + occupied

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"OccupancyData(free={self.free}, occupied={self.occupied}, "
            f"percentage={self.percentage:.2f}%)"
        )


class PhoenixBadApiClient:
    """API client for Phoenix-Bad Ottobrunn."""

    def __init__(
        self,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the API client.

        Args:
            session: Optional aiohttp session to use
            timeout: Request timeout in seconds
        """
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._own_session = session is None

    async def __aenter__(self) -> PhoenixBadApiClient:
        """Async context manager entry."""
        if self._own_session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._own_session and self._session:
            await self._session.close()

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._own_session and self._session:
            await self._session.close()

    async def _fetch_occupancy(self, url: str, area_name: str) -> OccupancyData:
        """Fetch occupancy data from API.

        Args:
            url: API endpoint URL
            area_name: Name of the area (for logging)

        Returns:
            OccupancyData object with parsed data

        Raises:
            PhoenixBadConnectionError: If connection fails
            PhoenixBadParseError: If parsing fails
        """
        if not self._session:
            raise PhoenixBadApiError("Session not initialized")

        _LOGGER.debug("Fetching %s occupancy data from %s", area_name, url)

        try:
            async with self._session.get(
                url, headers=DEFAULT_HEADERS, timeout=self._timeout
            ) as response:
                if response.status != 200:
                    error_msg = (
                        f"API returned status {response.status}: {response.reason}"
                    )
                    _LOGGER.error("Failed to fetch %s data: %s", area_name, error_msg)
                    raise PhoenixBadConnectionError(error_msg)

                text = await response.text()
                _LOGGER.debug("Raw %s response: %s", area_name, text.strip())

                return self._parse_response(text, area_name)

        except aiohttp.ClientError as err:
            error_msg = f"Connection error: {err}"
            _LOGGER.error("Failed to fetch %s data: %s", area_name, error_msg)
            raise PhoenixBadConnectionError(error_msg) from err
        except asyncio.TimeoutError as err:
            error_msg = "Request timeout"
            _LOGGER.error("Failed to fetch %s data: %s", area_name, error_msg)
            raise PhoenixBadConnectionError(error_msg) from err

    def _parse_response(self, html: str, area_name: str) -> OccupancyData:
        """Parse HTML response to extract occupancy data.

        Args:
            html: HTML response text
            area_name: Name of the area (for logging)

        Returns:
            OccupancyData object with parsed data

        Raises:
            PhoenixBadParseError: If parsing fails
        """
        try:
            soup = BeautifulSoup(html, "html.parser")

            # Find the outer wrapper div with data-free attribute
            # We first try the specific class, then fall back to any element with data-free
            outer_div = soup.find("div", class_="outer_wrapper") or soup.find(
                attrs={"data-free": True}
            )

            if not outer_div:
                if "Area data missing" in html:
                    _LOGGER.debug("%s area data missing (likely closed)", area_name)
                    return OccupancyData(free=0, occupied=0, percentage=0.0)

                # Log a snippet of the HTML to help debug future changes
                _LOGGER.error(
                    "Could not find occupancy data in %s response. HTML snippet: %s",
                    area_name,
                    html[:200],
                )
                raise PhoenixBadParseError(
                    f"Could not find occupancy data element in {area_name} response"
                )

            # Get free spaces from data-free attribute
            data_free = outer_div.get("data-free")
            if data_free is None:
                raise PhoenixBadParseError(
                    f"Could not find data-free attribute in {area_name} response"
                )

            if isinstance(data_free, list):
                data_free = data_free[0] if data_free else "0"

            try:
                free = int(str(data_free))
            except ValueError:
                _LOGGER.warning("Could not parse data-free attribute: %s", data_free)
                free = 0

            # Get occupied percentage from style attribute
            # We look for the inner_wrapper, but fall back to searching children for width
            inner_div = outer_div.find("div", class_="inner_wrapper") or outer_div.find(
                attrs={"style": re.compile(r"width")}
            )

            if not inner_div:
                # No visitors or different structure, try to find width in whole HTML
                width_match = re.search(r"width:\s*([\d.]+)%", html)
            else:
                style = str(inner_div.get("style", ""))
                width_match = re.search(r"width:\s*([\d.]+)%", style)

            if not width_match:
                # No width found, assume 0% occupancy
                _LOGGER.debug("%s has no width percentage, assuming 0%%", area_name)
                return OccupancyData(free=free, occupied=0, percentage=0.0)

            occupied_pct = float(width_match.group(1))

            # Calculate occupied count from percentage and free spaces
            # Formula: occupied = (occupied_pct * free) / (100 - occupied_pct)
            if occupied_pct >= 100:
                # Edge case: 100% occupancy
                occupied = free  # Assume total capacity = 2 * free
                _LOGGER.warning(
                    "%s shows 100%% occupancy, calculation may be inaccurate", area_name
                )
            else:
                occupied = round((occupied_pct * free) / (100 - occupied_pct))

            _LOGGER.debug(
                "%s data parsed: free=%d, occupied=%d, percentage=%.2f%%",
                area_name,
                free,
                occupied,
                occupied_pct,
            )

            return OccupancyData(free=free, occupied=occupied, percentage=occupied_pct)

        except (ValueError, AttributeError) as err:
            error_msg = f"Failed to parse {area_name} response: {err}"
            _LOGGER.error(error_msg)
            raise PhoenixBadParseError(error_msg) from err

    async def get_pool_occupancy(self) -> OccupancyData:
        """Get pool occupancy data."""
        return await self._fetch_occupancy(POOL_URL, "Pool")

    async def get_sauna_occupancy(self) -> OccupancyData:
        """Get sauna occupancy data."""
        return await self._fetch_occupancy(SAUNA_URL, "Sauna")

    async def get_all_occupancy(self) -> dict[str, OccupancyData]:
        """Get occupancy data for all areas."""
        pool_data, sauna_data = await asyncio.gather(
            self.get_pool_occupancy(),
            self.get_sauna_occupancy(),
            return_exceptions=True,
        )

        result: dict[str, OccupancyData] = {}

        if isinstance(pool_data, BaseException):
            _LOGGER.error("Failed to fetch pool data: %s", pool_data)
        else:
            result["pool"] = pool_data

        if isinstance(sauna_data, BaseException):
            _LOGGER.error("Failed to fetch sauna data: %s", sauna_data)
        else:
            result["sauna"] = sauna_data

        if not result:
            raise PhoenixBadConnectionError("Failed to fetch data for all areas")

        return result

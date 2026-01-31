import logging
import re
import aiohttp
from bs4 import BeautifulSoup
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=1)

SENSOR_TYPE_POOL = "pool"
SENSOR_TYPE_SAUNA = "sauna"

POOL_URL = "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateLiveVisitors&area=Bad"
SAUNA_URL = "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateLiveVisitors&area=Sauna"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


async def fetch_occupancy_generic(session, url, sensor_type):
    """Fetch occupancy data from the new HTML-based API."""
    _LOGGER.debug(f"Fetching {sensor_type} occupancy data from API...")
    try:
        async with session.get(url, headers=DEFAULT_HEADERS) as response:
            if response.status != 200:
                _LOGGER.error(f"Failed to fetch {sensor_type} data. Status: {response.status}, Reason: {response.reason}")
                _LOGGER.debug(f"Response text: {await response.text()}")
                return {sensor_type: (0, 0)}

            text = await response.text()
            _LOGGER.debug(f"Raw {sensor_type} response text: {text.strip()}")

            # Parse HTML response
            soup = BeautifulSoup(text, 'html.parser')

            # Find the outer wrapper div with data-free attribute
            outer_div = soup.find('div', class_='outer_wrapper')

            if not outer_div:
                _LOGGER.warning(f"Could not find outer_wrapper div for {sensor_type} data.")
                return {sensor_type: (0, 0)}

            # Get free spaces from data-free attribute
            data_free = outer_div.get('data-free')
            if not data_free:
                _LOGGER.warning(f"Could not find data-free attribute for {sensor_type} data.")
                return {sensor_type: (0, 0)}

            free = int(data_free)

            # Get occupied percentage from inner div style
            inner_div = outer_div.find('div', class_='inner_wrapper')
            if not inner_div:
                _LOGGER.warning(f"Could not find inner_wrapper div for {sensor_type} data.")
                return {sensor_type: (free, 0)}

            style = inner_div.get('style', '')
            width_match = re.search(r'width:\s*([\d.]+)%', style)

            if not width_match:
                _LOGGER.warning(f"Could not extract width percentage for {sensor_type} data.")
                return {sensor_type: (free, 0)}

            occupied_pct = float(width_match.group(1))

            # Calculate occupied count from percentage and free spaces
            # occupied_pct = (occupied / total) * 100
            # total = free + occupied
            # occupied = (occupied_pct * free) / (100 - occupied_pct)
            if occupied_pct >= 100:
                occupied = 0
                _LOGGER.warning(f"{sensor_type} shows 100% occupancy, setting occupied to 0")
            else:
                occupied = round((occupied_pct * free) / (100 - occupied_pct))

            _LOGGER.debug(f"{sensor_type} data fetched: free={free}, occupied={occupied}, occupancy={occupied_pct}%")
            return {sensor_type: (free, occupied)}

    except Exception as e:
        _LOGGER.error(f"Exception during {sensor_type} occupancy fetch: {e}")

    return {sensor_type: (0, 0)}


class PoolOccupancySensor(SensorEntity):
    """Representation of the pool occupancy sensor."""

    def __init__(self):
        self._attr_name = "Pool Occupancy"
        self._attr_unique_id = "phoenixbad_pool_occupancy"
        self._attr_entity_id = "sensor.phoenixbad_pool_occupancy"
        self._attr_unit_of_measurement = "%"
        self._attr_icon = "mdi:pool"
        self._attr_native_value = None
        self._free = 0
        self._occupied = 0
        self._attr_extra_state_attributes = {
            "source_url": POOL_URL,
            "attribution": f"Data provided by API {POOL_URL}"
        }

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def extra_state_attributes(self):
        return {
            "free": self._free,
            "occupied": self._occupied,
            "attribution": self._attr_extra_state_attributes["attribution"]
        }

    @property
    def should_poll(self):
        return True

    async def async_update(self):
        _LOGGER.debug("Updating PoolOccupancySensor...")
        async with aiohttp.ClientSession() as session:
            occupancy = await fetch_occupancy_generic(session, POOL_URL, SENSOR_TYPE_POOL)
            free, occupied = occupancy[SENSOR_TYPE_POOL]
            total = free + occupied

            self._free = free
            self._occupied = occupied
            self._attr_native_value = round((occupied / total) * 100) if total > 0 else 0

            _LOGGER.debug("PoolOccupancySensor updated: free=%s, occupied=%s, native_value=%s",
                          self._free, self._occupied, self._attr_native_value)


class SaunaOccupancySensor(SensorEntity):
    """Representation of the sauna occupancy sensor."""

    def __init__(self):
        self._attr_name = "Sauna Occupancy"
        self._attr_unique_id = "phoenixbad_sauna_occupancy"
        self._attr_entity_id = "sensor.phoenixbad_sauna_occupancy"
        self._attr_unit_of_measurement = "%"
        self._attr_icon = "mdi:waves"
        self._attr_native_value = None
        self._free = 0
        self._occupied = 0
        self._attr_extra_state_attributes = {
            "source_url": SAUNA_URL,
            "attribution": f"Data provided by API {SAUNA_URL}"
        }

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def extra_state_attributes(self):
        return {
            "free": self._free,
            "occupied": self._occupied,
            "attribution": self._attr_extra_state_attributes["attribution"]
        }

    @property
    def should_poll(self):
        return True

    async def async_update(self):
        _LOGGER.debug("Updating SaunaOccupancySensor...")
        async with aiohttp.ClientSession() as session:
            occupancy = await fetch_occupancy_generic(session, SAUNA_URL, SENSOR_TYPE_SAUNA)
            free, occupied = occupancy[SENSOR_TYPE_SAUNA]
            total = free + occupied

            self._free = free
            self._occupied = occupied
            self._attr_native_value = round((occupied / total) * 100) if total > 0 else 0

            _LOGGER.debug("SaunaOccupancySensor updated: free=%s, occupied=%s, native_value=%s",
                          self._free, self._occupied, self._attr_native_value)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Phönix Bad sensors from a config entry."""
    _LOGGER.debug("Setting up Phönix Bad sensors...")
    sensors = [
        PoolOccupancySensor(),
        SaunaOccupancySensor(),
    ]
    async_add_entities(sensors, update_before_add=True)
    _LOGGER.debug("Sensors added successfully.")

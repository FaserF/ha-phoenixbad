import logging
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

POOL_URL = "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateVisitors&area=hallenbad"
SAUNA_URL = "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateVisitors&area=sauna"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


async def fetch_occupancy_generic(session, url, sensor_type):
    """Generic fetch function that handles numeric or HTML responses."""
    _LOGGER.debug(f"Fetching {sensor_type} occupancy data from API...")
    try:
        async with session.get(url, headers=DEFAULT_HEADERS) as response:
            if response.status != 200:
                _LOGGER.error(f"Failed to fetch {sensor_type} data. Status: {response.status}, Reason: {response.reason}")
                _LOGGER.debug(f"Response text: {await response.text()}")
                return {sensor_type: (0, 0)}

            text = await response.text()
            _LOGGER.debug(f"Raw {sensor_type} response text: {text.strip()}")

            # Try if the response is just a number
            try:
                occupied = int(text.strip())
                _LOGGER.debug(f"{sensor_type.capitalize()} occupancy number found: occupied={occupied}")
                return {sensor_type: (0, occupied)}  # no free value known
            except ValueError:
                _LOGGER.debug(f"{sensor_type.capitalize()} response is not plain number, trying to parse HTML...")

            # Try parsing HTML
            soup = BeautifulSoup(text, 'html.parser')
            free_span = soup.find('span', title=True)
            occupied_div = soup.find('div', class_='inner_wrapper visitors')

            if free_span and occupied_div:
                free = int(free_span.text.strip() or "0")
                occupied_text = occupied_div.find('span', title=True)
                occupied = int(occupied_text.text.strip() or "0") if occupied_text else 0
                _LOGGER.debug(f"{sensor_type.capitalize()} data fetched: free={free}, occupied={occupied}")
                return {sensor_type: (free, occupied)}
            else:
                _LOGGER.warning(f"Could not find expected HTML structure for {sensor_type} data.")

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

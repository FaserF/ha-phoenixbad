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

async def fetch_occupancy_pool(session):
    """Fetch the occupancy data from the API."""
    _LOGGER.debug("Fetching pool occupancy data from API...")
    try:
        async with session.get(POOL_URL) as pool_response:
            pool_response.raise_for_status()
            pool_soup = BeautifulSoup(await pool_response.text(), 'html.parser')
            pool_free_span = pool_soup.find('span', title=True)
            pool_occupied_div = pool_soup.find('div', class_='inner_wrapper visitors')
            if pool_free_span and pool_occupied_div:
                pool_free = int(pool_free_span.text.strip() or "0")
                pool_occupied = int(pool_occupied_div.find('span', title=True).text.strip() or "0")
                _LOGGER.debug(f"Pool data fetched: free={pool_free}, occupied={pool_occupied}")
                return {SENSOR_TYPE_POOL: (pool_free, pool_occupied)}
            else:
                _LOGGER.error("Could not find required pool occupancy elements in the response.")
    except Exception as e:
        _LOGGER.error(f"Failed to fetch pool occupancy data: {e}")

    return {SENSOR_TYPE_POOL: (0, 0)}

async def fetch_occupancy_sauna(session):
    """Fetch the occupancy data from the API."""
    _LOGGER.debug("Fetching sauna occupancy data from API...")
    try:
        async with session.get(SAUNA_URL) as sauna_response:
            sauna_response.raise_for_status()
            sauna_soup = BeautifulSoup(await sauna_response.text(), 'html.parser')
            sauna_free_span = sauna_soup.find('span', title=True)
            sauna_occupied_div = sauna_soup.find('div', class_='inner_wrapper visitors')
            if sauna_free_span and sauna_occupied_div:
                sauna_free = int(sauna_free_span.text.strip() or "0")
                sauna_occupied = int(sauna_occupied_div.find('span', title=True).text.strip() or "0")
                _LOGGER.debug(f"Sauna data fetched: free={sauna_free}, occupied={sauna_occupied}")
                return {SENSOR_TYPE_SAUNA: (sauna_free, sauna_occupied)}
            else:
                _LOGGER.error("Could not find required sauna occupancy elements in the response.")
    except Exception as e:
        _LOGGER.error(f"Failed to fetch sauna occupancy data: {e}")

    return {SENSOR_TYPE_SAUNA: (0, 0)}

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
            occupancy = await fetch_occupancy_pool(session)
            if occupancy is None:
                _LOGGER.error("Occupancy data is None, cannot update sensor.")
                return

            free_pool, occupied_pool = occupancy[SENSOR_TYPE_POOL]
            total_pool = free_pool + occupied_pool

            self._free = free_pool
            self._occupied = occupied_pool
            self._attr_native_value = round((occupied_pool / total_pool) * 100) if total_pool > 0 else 0

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
            occupancy = await fetch_occupancy_sauna(session)
            if occupancy is None:
                _LOGGER.error("Occupancy data is None, cannot update sensor.")
                return

            free_sauna, occupied_sauna = occupancy[SENSOR_TYPE_SAUNA]
            total_sauna = free_sauna + occupied_sauna

            self._free = free_sauna
            self._occupied = occupied_sauna
            self._attr_native_value = round((occupied_sauna / total_sauna) * 100) if total_sauna > 0 else 0

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

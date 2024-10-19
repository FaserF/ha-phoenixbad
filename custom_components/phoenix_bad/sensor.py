import logging
import requests
from bs4 import BeautifulSoup  # Stelle sicher, dass du BeautifulSoup importierst
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_POOL = "pool"
SENSOR_TYPE_SAUNA = "sauna"

def fetch_occupancy():
    """Fetch the occupancy data from the API."""
    pool_url = "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateVisitors&area=hallenbad"
    sauna_url = "https://phoenixbad.de/wp-admin/admin-ajax.php?action=updateVisitors&area=sauna"

    occupancy_data = {}

    # Fetch pool occupancy
    _LOGGER.debug("Fetching pool occupancy data from API...")
    try:
        pool_response = requests.get(pool_url)
        pool_response.raise_for_status()  # Raise an error for bad responses
        pool_soup = BeautifulSoup(pool_response.text, 'html.parser')
        pool_free_span = pool_soup.find('span', title=True)
        pool_occupied_div = pool_soup.find('div', class_='inner_wrapper visitors')
        if pool_free_span is None or pool_occupied_div is None:
            _LOGGER.error("Could not find required pool occupancy elements in the response.")
            return None

        pool_free = int(pool_free_span.text.strip())
        pool_occupied = int(pool_occupied_div.find('span', title=True).text.strip())
        occupancy_data[SENSOR_TYPE_POOL] = (pool_free, pool_occupied)
        _LOGGER.debug(f"Pool data fetched: free={pool_free}, occupied={pool_occupied}")
    except requests.RequestException as e:
        _LOGGER.error(f"Failed to fetch pool occupancy data: {e}")
        return None

    # Fetch sauna occupancy
    _LOGGER.debug("Fetching sauna occupancy data from API...")
    try:
        sauna_response = requests.get(sauna_url)
        sauna_response.raise_for_status()  # Raise an error for bad responses
        sauna_soup = BeautifulSoup(sauna_response.text, 'html.parser')
        sauna_free_span = sauna_soup.find('span', title=True)
        sauna_occupied_div = sauna_soup.find('div', class_='inner_wrapper visitors')
        if sauna_free_span is None or sauna_occupied_div is None:
            _LOGGER.error("Could not find required sauna occupancy elements in the response.")
            return None

        sauna_free = int(sauna_free_span.text.strip())
        sauna_occupied = int(sauna_occupied_div.find('span', title=True).text.strip())
        occupancy_data[SENSOR_TYPE_SAUNA] = (sauna_free, sauna_occupied)
        _LOGGER.debug(f"Sauna data fetched: free={sauna_free}, occupied={sauna_occupied}")
    except requests.RequestException as e:
        _LOGGER.error(f"Failed to fetch sauna occupancy data: {e}")
        return None

    if occupancy_data:
        _LOGGER.debug(f"Occupancy data fetched successfully: {occupancy_data}")
    else:
        _LOGGER.error("Occupancy data is empty.")

    return occupancy_data

class PoolOccupancySensor(SensorEntity):
    """Representation of the pool occupancy sensor."""

    def __init__(self):
        self._attr_name = "Pool Occupancy"
        self._attr_unique_id = "phoenixbad_pool_occupancy"
        self._attr_entity_id = "sensor.phoenixbad_pool_occupancy"
        self._attr_unit_of_measurement = "%"
        self._attr_icon = "mdi:pool"
        self._attr_native_value = None
        self._attr_update_interval = timedelta(hours=1)

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def should_poll(self):
        return True

    async def async_update(self):
        _LOGGER.debug("Updating PoolOccupancySensor...")
        occupancy = fetch_occupancy()
        if occupancy is None:
            _LOGGER.error("Occupancy data is None, cannot update sensor.")
            return

        free_pool, occupied_pool = occupancy[SENSOR_TYPE_POOL]
        total_pool = free_pool + occupied_pool
        if total_pool > 0:
            self._attr_native_value = round((occupied_pool / total_pool) * 100, 2)
        else:
            self._attr_native_value = 0
            _LOGGER.error("Total pool capacity is zero, cannot calculate occupancy.")
        _LOGGER.debug("PoolOccupancySensor native_value updated to: %s", self._attr_native_value)

class SaunaOccupancySensor(SensorEntity):
    """Representation of the sauna occupancy sensor."""

    def __init__(self):
        self._attr_name = "Sauna Occupancy"
        self._attr_unique_id = "phoenixbad_sauna_occupancy"
        self._attr_entity_id = "sensor.phoenixbad_sauna_occupancy"
        self._attr_unit_of_measurement = "%"
        self._attr_icon = "mdi:waves"
        self._attr_native_value = None
        self._attr_update_interval = timedelta(hours=1)

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def should_poll(self):
        return True

    async def async_update(self):
        _LOGGER.debug("Updating SaunaOccupancySensor...")
        occupancy = fetch_occupancy()
        if occupancy is None:
            _LOGGER.error("Occupancy data is None, cannot update sensor.")
            return

        free_sauna, occupied_sauna = occupancy[SENSOR_TYPE_SAUNA]
        total_sauna = free_sauna + occupied_sauna
        if total_sauna > 0:
            self._attr_native_value = round((occupied_sauna / total_sauna) * 100, 2)
        else:
            self._attr_native_value = 0
            _LOGGER.error("Total sauna capacity is zero, cannot calculate occupancy.")
        _LOGGER.debug("SaunaOccupancySensor native_value updated to: %s", self._attr_native_value)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Phönix Bad sensors from a config entry."""
    _LOGGER.debug("Setting up Phönix Bad sensors...")
    try:
        # Create instances of the sensors and add them to Home Assistant
        sensors = [
            PoolOccupancySensor(),
            SaunaOccupancySensor(),
        ]

        _LOGGER.debug("Adding sensors: %s", [sensor.name for sensor in sensors])
        async_add_entities(sensors, update_before_add=True)
        _LOGGER.debug("Sensors added successfully.")
    except Exception as e:
        _LOGGER.error("Error setting up sensors: %s", e)
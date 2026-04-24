import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PhoenixBadCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up Phönix Bad sensors from a config entry."""
    _LOGGER.debug("Setting up Phönix Bad sensors...")
    coordinator: PhoenixBadCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        PoolOccupancySensor(coordinator),
        SaunaOccupancySensor(coordinator),
    ]
    async_add_entities(sensors)
    _LOGGER.debug("Sensors added successfully.")

class PhoenixBadSensor(CoordinatorEntity, SensorEntity):
    """Base class for Phoenix-Bad sensors."""
    
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: PhoenixBadCoordinator, sensor_type: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_unique_id = f"phoenixbad_{sensor_type}_occupancy"
        self._attr_unit_of_measurement = "%"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or self._sensor_type not in self.coordinator.data:
            return None
        return round(self.coordinator.data[self._sensor_type].percentage)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self.coordinator.data or self._sensor_type not in self.coordinator.data:
            return {}
        data = self.coordinator.data[self._sensor_type]
        return {
            "free": data.free,
            "occupied": data.occupied,
        }

class PoolOccupancySensor(PhoenixBadSensor):
    """Representation of the pool occupancy sensor."""
    def __init__(self, coordinator: PhoenixBadCoordinator):
        super().__init__(coordinator, "pool")
        self._attr_name = "Pool Occupancy"
        self._attr_icon = "mdi:pool"

class SaunaOccupancySensor(PhoenixBadSensor):
    """Representation of the sauna occupancy sensor."""
    def __init__(self, coordinator: PhoenixBadCoordinator):
        super().__init__(coordinator, "sauna")
        self._attr_name = "Sauna Occupancy"
        self._attr_icon = "mdi:waves"

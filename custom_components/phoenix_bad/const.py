"""Constants for the Phoenix-Bad Integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Final

# Integration domain
DOMAIN: Final = "phoenix_bad"

# Platforms
PLATFORMS: Final = ["sensor"]

# Configuration
DEFAULT_SCAN_INTERVAL: Final = timedelta(hours=1)
MIN_SCAN_INTERVAL: Final = timedelta(minutes=5)
MAX_SCAN_INTERVAL: Final = timedelta(hours=24)

# Sensor types
SENSOR_TYPE_POOL: Final = "pool"
SENSOR_TYPE_SAUNA: Final = "sauna"

# Sensor keys
SENSOR_KEY_POOL_OCCUPANCY: Final = "pool_occupancy"
SENSOR_KEY_SAUNA_OCCUPANCY: Final = "sauna_occupancy"
SENSOR_KEY_POOL_FREE: Final = "pool_free"
SENSOR_KEY_SAUNA_FREE: Final = "sauna_free"
SENSOR_KEY_POOL_OCCUPIED: Final = "pool_occupied"
SENSOR_KEY_SAUNA_OCCUPIED: Final = "sauna_occupied"

# Device info
MANUFACTURER: Final = "Phoenix-Bad Ottobrunn"
MODEL: Final = "Occupancy Sensor"
DEVICE_NAME: Final = "Phoenix-Bad Ottobrunn"

# URLs
WEBSITE_URL: Final = "https://phoenixbad.de"

# Configuration options
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Attributes
ATTR_FREE: Final = "free"
ATTR_OCCUPIED: Final = "occupied"
ATTR_TOTAL: Final = "total"
ATTR_PERCENTAGE: Final = "percentage"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_AREA: Final = "area"

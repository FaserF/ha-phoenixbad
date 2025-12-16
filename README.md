[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Phönix Bad Home Assistant Sensor 🏊

The `phoenix_bad` sensor provides real-time occupancy information for the **Phönix Bad Ottobrunn**.

## Features ✨

- **Occupancy Tracking**: Know how busy the pool or sauna is before you go.

## Installation 🛠️

### 1. Using HACS (Recommended)

This integration works as a **Custom Repository** in HACS.

1.  Open HACS.
2.  Add Custom Repository: `https://github.com/FaserF/ha-phoenixbad` (Category: Integration).
3.  Click **Download**.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FaserF&repository=ha-phoenixbad&category=integration)

### 2. Manual Installation

1.  Download the latest [Release](https://github.com/FaserF/ha-phoenixbad/releases/latest).
2.  Extract the ZIP file.
3.  Copy the `phoenix_bad` folder to `<config>/custom_components/`.

## Configuration ⚙️

1.  Go to **Settings** -> **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for "Phönix Bad Ottobrunn".

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=phoenix_bad)

### Configuration Variables
None needed.

## Bug reporting
Open an issue over at [github issues](https://github.com/FaserF/ha-phoenixbad/issues). Please prefer sending over a log with debugging enabled.

To enable debugging enter the following in your configuration.yaml

```yaml
logger:
    logs:
        custom_components.phoenix_bad: debug
```

You can then find the log in the HA settings -> System -> Logs -> Enter "phoenix_bad" in the search bar -> "Load full logs"

## Thanks to
The data is coming from the corresponding [phoenixbad.de](https://phoenixbad.de/) website.
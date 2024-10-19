[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
# Phönix Bad Ottobrunn occupancy Homeassistant Sensor
The `phoenix_bad` sensor will give you informations about the current utilization of a phoenix_bad hall

## Installation
### 1. Using HACS (recommended way)

This integration is soon a official HACS Integration.

Open HACS then install the "Phönix Bad Ottobrunn" integration or use the link below.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FaserF&repository=ha-phoenixbad&category=integration)

If you use this method, your component will always update to the latest version.

### 2. Manual

- Download the latest zip release from [here](https://github.com/FaserF/ha-phoenixbad/releases/latest)
- Extract the zip file
- Copy the folder "phoenix_bad" from within custom_components with all of its components to `<config>/custom_components/`

where `<config>` is your Home Assistant configuration directory.

>__NOTE__: Do not download the file by using the link above directly, the status in the "master" branch can be in development and therefore is maybe not working.

## Configuration

Go to Configuration -> Integrations and click on "add integration". Then search for "Phönix Bad Ottobrunn".

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
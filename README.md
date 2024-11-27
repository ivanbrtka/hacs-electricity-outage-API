# Power Outage Checker

This is a custom integration for Home Assistant to notifying user of any electricity outage in 30 days.

## Installation

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository.
3. Search for "Power Outage Checker" and install it.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: my_power_outages
    latitude: 48.1486
    longitude: 17.1077
```
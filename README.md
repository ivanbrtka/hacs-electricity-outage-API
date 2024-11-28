# Power Outage Checker

This custom integration for Home Assistant provides notifications about upcoming electricity outages within the next 30 days. It is designed specifically for the Slovakia region, covering both eastern and western Slovakia. The integration automatically retrieves data from an API based on the current location of your Home Assistant instance.

## Installation

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository.
3. Search for "Power Outage Checker" and install it.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: power_outages
```

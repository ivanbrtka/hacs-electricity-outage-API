from datetime import datetime
import requests
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "power_outages"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the power_outages sensor."""
    latitude = hass.config.latitude
    longitude = hass.config.longitude

    if latitude is None or longitude is None:
        _LOGGER.error("Home Assistant configuration lacks latitude or longitude.")
        return

    async_add_entities([PowerOutageSensor(latitude, longitude)])

class PowerOutageSensor(SensorEntity):
    """Representation of a Power Outage Sensor."""

    def __init__(self, latitude, longitude):
        """Initialize the sensor."""
        self._latitude = latitude
        self._longitude = longitude
        self._state = None
        self._attributes = {}
        self._unique_id = f"power_outage_sensor_{latitude}_{longitude}".replace(".", "_")

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Next Power Outage"

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return additional attributes of the sensor."""
        return self._attributes

    def update(self):
        """Fetch new data from the API."""
        try:
            REVERSE_GPS_URL = (
                f"https://nominatim.openstreetmap.org/reverse.php?lat={self._latitude}&lon={self._longitude}&zoom=18&format=jsonv2"
            )
            OUTAGE_API_URL = "https://www.vypadokelektriny.sk/api/data/outages30days/address"

            headers = {
                "User-Agent": "Mozilla/5.0 (HomeAssistant Integration)",
                "Content-Type": "application/json",
            }

            # Fetch address data using reverse GPS lookup
            gps_response = requests.get(REVERSE_GPS_URL, headers=headers, timeout=10)
            gps_data = gps_response.json()
            postcode = gps_data["address"]["postcode"].replace(" ", "")
            city = gps_data["address"].get("village", gps_data["address"].get("town", ""))

            # Prepare outage request payload
            payload = {
                "data": {
                    "OBEC": city,
                    "PSC": postcode,
                    "ULICA": "",
                    "CISLO_DOMU": "",
                    "EIC": "",
                    "CISLO_ELEKTROMERA": "",
                }
            }

            # Fetch outage data
            outage_response = requests.post(
                OUTAGE_API_URL, json=payload, headers=headers, timeout=10
            )
            outage_data = outage_response.json()

            if outage_data:
                next_outage = outage_data[0]
                self._state = "Outage detected"
                self._attributes = {
                    "next_outage_start": next_outage["realStart"],
                    "next_outage_end": next_outage["realEnd"],
                }
            else:
                self._state = "No outages"
                self._attributes = {"message": "No outages in the next 30 days"}

        except Exception as e:
            _LOGGER.error("Error fetching power outage data: %s", e)
            self._state = "Error"
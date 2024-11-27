from datetime import datetime, timedelta
import requests, logging, json

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE

_LOGGER = logging.getLogger(__name__)

# Basic sensor setup
async def async_setup(hass, config, async_add_entities, discovery_info=None):
    
    # Use GPS data from Home Assistant config data
    latitude = hass.config.latitude
    longitude = hass.config.longitude

    async_add_entities([PowerOutageSensor(latitude, longitude)])

# Sensor used for representing next electricity outage
class PowerOutageSensor(SensorEntity):

    # Define basic attributes
    def __init__(self, latitude, longitude):
        self._latitude = latitude
        self._longitude = longitude
        self._state = None
        self._attributes = {}

    # Sensor name
    @property
    def name(self):
        return "Next power outage on your address"

    # Sensor state
    @property
    def state(self):
        return self._state


    # Extra attributes
    @property
    def extra_state_attributes(self):
        return self._attributes

    # Fetch new data from API 
    def update(self):
        
        # URL of power outage data API and reverse GPS Lookup API
        REVERSE_GPS_URL=f"https://nominatim.openstreetmap.org/reverse.php?lat={self._latitude}&lon={self._longtitude}&zoom=18&format=jsonv2"
        OUTAGE_API_URL="https://www.vypadokelektriny.sk/api/data/outages30days/address"

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            gps_data = requests.get(REVERSE_GPS_URL, headers=headers, timeout=10)
            gps_data_json = json.loads(gps_data.text)

            postcode = gps_data_json['address']['postcode']
            city = gps_data_json['address']['village']
            postcode = postcode.replace(" ", "")

            home_location_params = {
                "data": {
                    "OBEC":f"{city}",
                    "PSC":f"{postcode}",
                    "ULICA":"",
                    "CISLO_DOMU":"",
                    "EIC":"",
                    "CISLO_ELEKTROMERA":""  
                    }
                }
            response = requests.post(OUTAGE_API_URL, json=home_location_params, headers=headers, timeout=10)
            response.raise_for_status()

            outage_data_json = json.loads(response.text)

            if outage_data_json:
                next_electricity_outage_start = outage_data_json[0]['realStart']
                next_electricity_outage_end = outage_data_json[0]['realEnd']
                self._state = "Outage detected"
                self._attributes = {
                    "next_outage_start": next_electricity_outage_start,
                    "next_outage_end": next_electricity_outage_end,
                }
            else:
                self._state = "No outages"
                self._attributes = {"message": "No outages in the next 30 days"}
        
        except Exception as e:
            _LOGGER.error("Error fetching power outage data: %s", e)
            self._state = "Error"

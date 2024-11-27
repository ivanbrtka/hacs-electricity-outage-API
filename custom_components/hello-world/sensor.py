from datetime import datetime, timedelta
import requests, logging, json

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
_LOGGER = logging.getLogger(__name__)

DOMAIN="power_outages"

# Basic sensor setup
def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    
    # Use GPS data from Home Assistant config data
    latitude = hass.config.latitude
    longitude = hass.config.longitude

    add_entities([PowerOutageSensorStart(latitude, longitude)])
    add_entities([PowerOutageSensorEnd(latitude, longitude)])

# Sensor used for representing next electricity outage
class PowerOutageSensorStart(SensorEntity):

    # Define basic attributes
    _attr_name = "Next Power Outage Start Date"
    _attr_device_class = SensorDeviceClass.DATE
    _attr_state_class = None

    def update(self):     
        # URL of power outage data API and reverse GPS Lookup API
        REVERSE_GPS_URL=f"https://nominatim.openstreetmap.org/reverse.php?lat={self.latitude}&lon={self.longitude}&zoom=18&format=jsonv2"
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
                self._attr_native_value = datetime.strptime(next_electricity_outage_start, '%Y-%m-%dT%H:%M:%S%z')
                
        
        except Exception as e:
            _LOGGER.error("Error fetching power outage data: %s", e)
            self._state = "Error"         


# Sensor used for representing next electricity outage
class PowerOutageSensorEnd(SensorEntity):

    # Define basic attributes
    _attr_name = "Next Power Outage End Date"
    _attr_device_class = SensorDeviceClass.DATE
    _attr_state_class = None

    def update(self):
        # URL of power outage data API and reverse GPS Lookup API
        REVERSE_GPS_URL=f"https://nominatim.openstreetmap.org/reverse.php?lat={self.latitude}&lon={self.longitude}&zoom=18&format=jsonv2"
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
                next_electricity_outage_end = outage_data_json[0]['realEnd']
                self._attr_native_value = datetime.strptime(next_electricity_outage_end, '%Y-%m-%dT%H:%M:%S%z')
                
        
        except Exception as e:
            _LOGGER.error("Error fetching power outage data: %s", e)
            self._state = "Error"      


'''
    # Fetch new data from API 
    def update(self):
        
        # URL of power outage data API and reverse GPS Lookup API
        REVERSE_GPS_URL=f"https://nominatim.openstreetmap.org/reverse.php?lat={self._latitude}&lon={self._longitude}&zoom=18&format=jsonv2"
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
    '''
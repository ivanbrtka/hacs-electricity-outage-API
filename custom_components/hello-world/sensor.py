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

# Initiate logger
_LOGGER = logging.getLogger(__name__)

# Define domain
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

    # Create new instances of sensors
    add_entities([PowerOutageSensorStart(latitude, longitude)])
    add_entities([PowerOutageSensorEnd(latitude, longitude)])

# Sensor used for representing next electricity outage
class PowerOutageSensorStart(SensorEntity):

    # Define basic attributes
    _attr_name = "Next Power Outage Start Date"
    _attr_device_class = SensorDeviceClass.DATE
    _attr_state_class = None

    # Start date sensor constructor
    def __init__(self, latitude, longitude):

        # Call constructor of parent class
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude
        self._attr_native_value = None
        self._formatted_date = None
        self._attr_unique_id = f"power_outage_end_{latitude}_{longitude}"

    # Update value of sensor
    def update(self):
        dt = fetch_data_from_api(self.latitude, self.longitude, False) 
        self._attr_native_value = dt
        if dt:
            self._formatted_date = dt.strftime("%A, %B %d, %Y, %I:%M %p")

    @property
    def extra_state_attributes(self):
        return {
            "formatted_date": self._formatted_date
        }    

# Sensor used for representing next electricity outage
class PowerOutageSensorEnd(SensorEntity):

    # Define basic attributes
    _attr_name = "Next Power Outage End Date"
    _attr_device_class = SensorDeviceClass.DATE
    _attr_state_class = None

     # End date sensor constructor
    def __init__(self, latitude, longitude):

         # Call constructor of parent class
        super().__init__()
        self.latitude = latitude
        self.longitude = longitude
        self._attr_native_value = None
        self._formatted_date = None
        self._attr_unique_id = f"power_outage_start_{latitude}_{longitude}"

    # Update value of sensor
    def update(self):
        dt = fetch_data_from_api(self.latitude, self.longitude, False) 
        self._attr_native_value = dt
        if dt:
            self._formatted_date = dt.strftime("%A, %B %d, %Y, %I:%M %p")

    @property
    def extra_state_attributes(self):
        return {
            "formatted_date": self._formatted_date
        }    


# Get location data from HA configuration and request additional geolocation data from API. Based on this data, call API for upcoming power outages on your location
def fetch_data_from_api(latitude, longitude, start):
    # URL of power outage data API and reverse GPS Lookup API
    REVERSE_GPS_URL=f"https://nominatim.openstreetmap.org/reverse.php?lat={latitude}&lon={longitude}&zoom=18&format=jsonv2"
    OUTAGE_API_URL="https://www.vypadokelektriny.sk/api/data/outages30days/address"

    try:
        # Set headers for valid request and parse request as JSON
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-Type': 'application/json'}
        gps_data = requests.get(REVERSE_GPS_URL, headers=headers, timeout=10)
        gps_data_json = json.loads(gps_data.text)

        # Get basic location informations from data and remove space in postcode
        postcode = gps_data_json['address']['postcode']
        postcode = postcode.replace(" ", "")

        city = None
        dt = None

        # Get name of the city if API returns its name in key village
        try:
            city = gps_data_json['address']['village']
        except:
            pass

        # Get name of the city if API returns its name in key city
        try:
            city = gps_data_json['address']['city']
        except:
            pass
        
        # Data structure for electricity outage API
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
        
        # Send POST request to API and fetch response
        response = requests.post(OUTAGE_API_URL, json=home_location_params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse outage data to JSON
        outage_data_json = json.loads(response.text)

        # If data exists, select start or end date based on selection
        if outage_data_json:
            if start:
                next_electricity_outage = outage_data_json[0]['start']
            else: 
                next_electricity_outage = outage_data_json[0]['end']

            # Append a timezone offset if missing
            if next_electricity_outage[-1] != 'Z' and '+' not in next_electricity_outage:
                next_electricity_outage += '+01:00'         
            
            # Try to parse date string into datetime python data type
            try:
                dt = datetime.strptime(next_electricity_outage, '%Y-%m-%dT%H:%M:%S%z')
            except Exception as e:
                _LOGGER.error("Date format error: %s", e)

            return dt
        
        # If no data exists, return None
        else: 
            return None
    
    # Case of error
    except Exception as e:
        _LOGGER.error("Error fetching power outage data: %s", e)
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import TEMP_CELSIUS
import requests
import json

DOMAIN = "home_simulator"
SENSOR_DATA_URL = "https://iammeter.rovnehome.online/monitorjson"  # Replace with your actual data source

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    sensors = [
        HomeSimulatorSensor("Voltage", 0),
        HomeSimulatorSensor("Current", 1),
        HomeSimulatorSensor("Power", 2),
        HomeSimulatorSensor("Energy", 3),
        HomeSimulatorSensor("Frequency", 5),
        HomeSimulatorSensor("Power Factor", 6),
    ]
    async_add_entities(sensors, update_before_add=True)

class HomeSimulatorSensor(SensorEntity):
    def __init__(self, name, index):
        """Initialize the sensor."""
        self._name = f"Home Simulator {name}"
        self._index = index
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        """Fetch new state data for the sensor."""
        try:
            response = requests.get(SENSOR_DATA_URL, timeout=10)
            data = response.json()

            # Fetch the data array we are interested in
            self._state = data["Datas"][0][self._index]  # First entry in "Datas" list, index specified
            self._attributes = {
                "SN": data.get("SN"),
                "MAC": data.get("mac"),
                "Version": data.get("version"),
            }

        except Exception as e:
            self._state = None
            self._attributes = {"error": str(e)}

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "power_outages"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the integration."""
    # Register a service for updating location
    hass.data[DOMAIN] = {}
    return True
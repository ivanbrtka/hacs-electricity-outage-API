from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.discovery import load_platform

DOMAIN = "power_outages"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the integration."""
    # Register a service for updating location
    load_platform("sensor", DOMAIN, {}, config)
    return True
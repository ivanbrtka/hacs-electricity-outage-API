from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "power_outages"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the power outages integration."""
    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, config)
    return True
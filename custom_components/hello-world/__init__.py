from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "power_outages"

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the power_outages integration."""
    hass.data[DOMAIN] = {}  # Uložíme stav pre integráciu (voliteľné)
    return True
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "power_outages"

async def async_setup(hass: HomeAssistant, config: dict):
    """Legacy setup - does nothing."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration using config flow."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload the integration."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
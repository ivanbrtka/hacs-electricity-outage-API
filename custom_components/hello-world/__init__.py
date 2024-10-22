import logging

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    _LOGGER.info("Hello World from the custom component!")
    return True

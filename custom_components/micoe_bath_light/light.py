"""Support for HomeSeer light-type devices."""
import asyncio
import logging
from typing import Any

from homeassistant.components.light import (
    ToggleEntity, LightEntity

)
from homeassistant.const import (
    CONF_NAME, STATE_ON, STATE_OFF
)
from .command import (turn_off, turn_light_up)

_LOGGER = logging.getLogger(__name__)
LIGHT_PLATFORMS = ["light"]


async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Perform the setup for Beverly water purifier."""

    light_entities = []

    light = MicoeLight(hass, config.get(CONF_NAME))
    light_entities.append(light)

    _LOGGER.warn('async_setup_platform')

    async_add_devices(light_entities)


class MicoeLight(LightEntity):
    """Representation of a HomeSeer light-type device."""

    def __init__(self, hass, name):
        self._hass = hass
        self._name = name

        self._attr_is_on = False

    @property
    def icon(self):
        return 'hass:lightbulb'

    @property
    def name(self):
        return self._name

    def turn_on(self, **kwargs: Any) -> None:
        turn_light_up('Light')
        self._attr_is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        turn_off()
        self._attr_is_on = False

import logging
import asyncio
import threading
import voluptuous as vol
from homeassistant.helpers.event import async_track_state_change
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import (
    PLATFORM_SCHEMA,
    PLATFORM_SCHEMA_BASE,
)
from homeassistant.components.select import (
    SelectEntity,
    DOMAIN,
)


from homeassistant.const import (
    CONF_NAME,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
    STATE_OFF,
)
from typing import List

import serial as ser
se = ser.Serial("/dev/cu.usbserial-1410")

_LOGGER = logging.getLogger(__name__)

CONFIG_SWITCH_LIGHT = 'switch_light'
CONFIG_SWITCH_NIGHT_LIGHT = 'switch_night_light'
CONFIG_SWITCH_NATURE_WIND = 'switch_nature_wind'

CONFIG_SWITCH_OFF = 'switch_off'
CONFIG_SWITCH_HEAT = 'switch_heat'
CONFIG_SWITCH_VENTILATE = 'switch_ventilate'
CONFIG_SWITCH_COOL = 'switch_cool'
CONFIG_SWITCH_DRY = 'switch_dry'

CONFIG_SENSOR_LIGHT = 'sensor_light'
CONFIG_SENSOR_NIGHT_LIGHT = 'sensor_night_light'
CONFIG_SENSOR_NATURE_WIND = 'sensor_nature_wind'

CONFIG_SENSOR_OFF = 'sensor_off'
CONFIG_SENSOR_HEAT = 'sensor_heat'
CONFIG_SENSOR_VENTILATE = 'sensor_ventilate'
CONFIG_SENSOR_COOL = 'sensor_cool'
CONFIG_SENSOR_DRY = 'sensor_dry'

DEFAULT_OPTION = 'Off'
OPTIONS = ['Off', 'Heat', 'Ventilate', 'Cool', 'Dry', 'Light', 'Night Light', 'Nature Wind']
ICON = 'mdi:fan'


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONFIG_SWITCH_OFF): cv.string,
    vol.Required(CONFIG_SWITCH_HEAT): cv.string,
    vol.Required(CONFIG_SWITCH_VENTILATE): cv.string,
    vol.Required(CONFIG_SWITCH_COOL): cv.string,
    vol.Required(CONFIG_SWITCH_DRY): cv.string,
    vol.Required(CONFIG_SENSOR_OFF): cv.string,
    vol.Required(CONFIG_SENSOR_HEAT): cv.string,
    vol.Required(CONFIG_SENSOR_VENTILATE): cv.string,
    vol.Required(CONFIG_SENSOR_COOL): cv.string,
    vol.Required(CONFIG_SENSOR_DRY): cv.string,

    vol.Required(CONFIG_SWITCH_LIGHT): cv.string,
    vol.Required(CONFIG_SWITCH_NIGHT_LIGHT): cv.string,
    vol.Required(CONFIG_SWITCH_NATURE_WIND): cv.string,
    vol.Required(CONFIG_SENSOR_LIGHT): cv.string,
    vol.Required(CONFIG_SENSOR_NIGHT_LIGHT): cv.string,
    vol.Required(CONFIG_SENSOR_NATURE_WIND): cv.string,
})


@asyncio.coroutine
def async_setup_platform(hass, config, add_devices_callback, discovery_info=None):
    name = config.get(CONF_NAME)
    add_devices_callback([WarmbathFan(hass, config, name)])


class WarmbathFan(SelectEntity):
    def __init__(self, hass, config, name):
        """Initialize the generic device."""
        self._hass = hass
        self.timer = None
        self._name = name
        self._default_state = DEFAULT_OPTION
        self._attr_current_option = self._default_state
        self._attr_options = OPTIONS
        self._entity_map = {
            'Off': config.get(CONFIG_SWITCH_OFF),
            'Heat': config.get(CONFIG_SWITCH_HEAT),
            'Ventilate': config.get(CONFIG_SWITCH_VENTILATE),
            'Cool': config.get(CONFIG_SWITCH_COOL),
            'Dry': config.get(CONFIG_SWITCH_DRY),

            'Light': config.get(CONFIG_SWITCH_LIGHT),
            'Night Light': config.get(CONFIG_SWITCH_NIGHT_LIGHT),
            'Nature Wind': config.get(CONFIG_SWITCH_NATURE_WIND),
        }

        self._hex_map = {
            'Off': 'FD 03 51 B6 0C 49 DF',
            'Heat': 'FD 03 51 B6 04 48 DF',
            'Ventilate': 'FD 03 51 B6 01 49 DF',
            'Cool': '',
            'Dry': '',

            'Light': 'FD 03 51 B6 08 48 DF ',
            'Night Light': 'FD 03 51 B6 02 49 DF',
            'Nature Wind': 'FD 03 51 B6 03 49 DF',
        }
        self._state_map = {
            config.get(CONFIG_SENSOR_OFF): 'Off',
            config.get(CONFIG_SENSOR_HEAT): 'Heat',
            config.get(CONFIG_SENSOR_VENTILATE): 'Ventilate',
            config.get(CONFIG_SENSOR_COOL): 'Cool',
            config.get(CONFIG_SENSOR_DRY): 'Dry',

            config.get(CONFIG_SENSOR_LIGHT): 'Light',
            config.get(CONFIG_SENSOR_NIGHT_LIGHT): 'Night Light',
            config.get(CONFIG_SENSOR_NATURE_WIND): 'Nature Wind',
        }
        tracking_ids = [
            config.get(CONFIG_SENSOR_OFF),
            config.get(CONFIG_SENSOR_HEAT),
            config.get(CONFIG_SENSOR_VENTILATE),
            config.get(CONFIG_SENSOR_COOL),
            config.get(CONFIG_SENSOR_DRY),

            config.get(CONFIG_SENSOR_LIGHT),
            config.get(CONFIG_SENSOR_NIGHT_LIGHT),
            config.get(CONFIG_SENSOR_NATURE_WIND)
        ]
        async_track_state_change(
            hass=hass,
            entity_ids=tracking_ids,
            action=self.device_state_changed_listener,
            from_state=STATE_OFF,
            to_state=STATE_ON,
        )

    @property
    def should_poll(self):
        """Poll the device."""
        return True

    @property
    def icon(self):
        """Return the icon for device by its type."""
        return ICON

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def options(self) -> List[str]:
        """Return a set of selectable options."""
        return self._attr_options

    @property
    def current_option(self) -> str:
        """Return the selected entity option to represent the entity state."""
        return self._attr_current_option

    def select_option(self, option: str) -> None:
        entity_id = self._entity_map.get(option)
        self.hass.services.call('switch', SERVICE_TURN_ON, {'entity_id': entity_id})
        self._attr_current_option = option

        toBytes = bytes.fromhex(self._hex_map.get(option))
        res = se.write(toBytes)
        _LOGGER.warn(res)

        self.count_down()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.hass.async_add_executor_job(self.select_option, option)

    def device_state_changed_listener(self, entity_id, from_s, to_s):
        self._attr_current_option = self._state_map.get(entity_id)
        self.async_write_ha_state()
        self.count_down()

    def count_down(self) -> None:
        if self._attr_current_option != DEFAULT_OPTION:
            self.timer = threading.Timer(60 * 15, self.auto_turn_off)
            self.timer.start()

    def auto_turn_off(self) -> None:
        _LOGGER.debug("auto turn off warmbath in 15 mins")
        self._attr_current_option = DEFAULT_OPTION
        self.async_write_ha_state()
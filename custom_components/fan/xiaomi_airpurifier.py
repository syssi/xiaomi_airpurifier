"""
Support for Xiaomi Mi Air Purifier 2.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/switch.xiaomi_airpurifier/
"""
import asyncio
from functools import partial
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.components.fan import (FanEntity, PLATFORM_SCHEMA, SUPPORT_SET_SPEED, )
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, )
from homeassistant.exceptions import PlatformNotReady

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Xiaomi Air Purifier'
PLATFORM = 'xiaomi_airpurifier'
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

#REQUIREMENTS = ['python-mirobo']
REQUIREMENTS = ['https://github.com/rytilahti/python-mirobo/archive/'
                '168f5c0ff381b3b02cedd0917597195b3c521a20.zip#'
                'python-mirobo']

ATTR_TEMPERATURE = 'temperature'
ATTR_HUMIDITY = 'humidity'
ATTR_AIR_QUALITY_INDEX = 'aqi'
ATTR_MODE = 'mode'
ATTR_FILTER_HOURS_USED = 'filter_hours_used'
ATTR_FILTER_LIFE = 'filter_life_remaining'
ATTR_FAVORITE_LEVEL = 'favorite_level'
ATTR_BUZZER = 'buzzer'
ATTR_CHILD_LOCK = 'child_lock'
ATTR_LED = 'led'
ATTR_LED_BRIGHTNESS = 'led_brightness'
ATTR_MOTOR_SPEED = 'motor_speed'

SUCCESS = ['ok']


# pylint: disable=unused-argument
@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the air purifier from config."""
    from mirobo import AirPurifier, DeviceException
    if PLATFORM not in hass.data:
        hass.data[PLATFORM] = {}

    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    _LOGGER.info("Initializing with host %s (token %s...)", host, token[:5])

    try:
        air_purifier = AirPurifier(host, token)

        xiaomi_air_purifier = XiaomiAirPurifier(name, air_purifier)
        hass.data[PLATFORM][host] = xiaomi_air_purifier
    except DeviceException:
        raise PlatformNotReady

    async_add_devices([xiaomi_air_purifier], update_before_add=True)


class XiaomiAirPurifier(FanEntity):
    """Representation of a Xiaomi Air Purifier."""

    def __init__(self, name, air_purifier):
        """Initialize the air purifier."""
        self._name = name

        self._air_purifier = air_purifier
        self._state = None
        self._state_attrs = {
            ATTR_AIR_QUALITY_INDEX: None,
            ATTR_TEMPERATURE: None,
            ATTR_HUMIDITY: None,
            ATTR_MODE: None,
            ATTR_FILTER_HOURS_USED: None,
            ATTR_FILTER_LIFE: None,
            ATTR_FAVORITE_LEVEL: None,
            ATTR_BUZZER: None,
            ATTR_CHILD_LOCK: None,
            ATTR_LED: None,
            ATTR_LED_BRIGHTNESS: None,
            ATTR_MOTOR_SPEED: None
        }

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_SET_SPEED

    @property
    def should_poll(self):
        """Poll the fan."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return self._state is not None

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if fan is on."""
        return self._state

    @asyncio.coroutine
    def _try_command(self, mask_error, func, *args, **kwargs):
        """Call a air purifier command handling error messages."""
        from mirobo import DeviceException
        try:
            result = yield from self.hass.async_add_job(
                partial(func, *args, **kwargs))

            _LOGGER.debug("Response received from air purifier: %s", result)

            return result == SUCCESS
        except DeviceException as exc:
            _LOGGER.error(mask_error, exc)
            return False

    @asyncio.coroutine
    def async_turn_on(self: ToggleEntity, speed: str=None, **kwargs) -> None:
        """Turn the fan on."""

        if speed:
            # Assumption: If operation mode was set the device must not be turned on explicit
            yield from self.async_set_speed(speed)
            return

        result = yield from self._try_command(
            "Turning the air purifier on failed.", self._air_purifier.on)

        if result:
            self._state = True

    @asyncio.coroutine
    def async_turn_off(self: ToggleEntity, **kwargs) -> None:
        """Turn the fan off."""
        result = yield from self._try_command(
            "Turning the air purifier off failed.", self._air_purifier.off)

        if result:
            self._state = False

    @asyncio.coroutine
    def async_update(self):
        """Fetch state from the device."""
        from mirobo import DeviceException

        try:
            state = yield from self.hass.async_add_job(self._air_purifier.status)
            _LOGGER.debug("Got new state: %s", state.data)

            self._state = state.is_on
            self._state_attrs = {
                ATTR_TEMPERATURE: state.temperature,
                ATTR_HUMIDITY: state.humidity,
                ATTR_AIR_QUALITY_INDEX: state.aqi,
                ATTR_MODE: state.mode.value,
                ATTR_FILTER_HOURS_USED: state.filter_hours_used,
                ATTR_FILTER_LIFE: state.filter_life_remaining,
                ATTR_FAVORITE_LEVEL: state.favorite_level,
                ATTR_BUZZER: state.buzzer,
                ATTR_CHILD_LOCK: state.child_lock,
                ATTR_LED: state.led,
                ATTR_LED_BRIGHTNESS: state.led_brightness.value,
                ATTR_MOTOR_SPEED: state.motor_speed
            }

        except DeviceException as ex:
            _LOGGER.error("Got exception while fetching the state: %s", ex)

    @property
    def speed_list(self: ToggleEntity) -> list:
        """Get the list of available speeds."""
        from mirobo.airpurifier import OperationMode
        supported_speeds = list()
        for mode in OperationMode:
            supported_speeds.append(mode.name)

        return supported_speeds

    @property
    def speed(self):
        """Return the current speed."""
        if self._state:
            from mirobo.airpurifier import OperationMode

            return OperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    @asyncio.coroutine
    def async_set_speed(self: ToggleEntity, speed: str) -> None:
        """Set the speed of the fan."""
        _LOGGER.debug("Setting the operation mode to: " + speed)
        from mirobo.airpurifier import OperationMode

        result = yield from self._try_command(
            "Setting operation mode of the air purifier failed.", self._air_purifier.set_mode, OperationMode[speed])

        if result:
            self._state_attrs[ATTR_MODE] = OperationMode[speed].value
            if speed == OperationMode.idle.name:
                # Setting the operation mode "idle" will turn off the device(?)
                self._state = False
            else:
                self._state = True

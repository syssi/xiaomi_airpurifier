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
from homeassistant.components.fan import (FanEntity, PLATFORM_SCHEMA, )
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

REQUIREMENTS = ['python-mirobo==0.1.3']

ATTR_POWER = 'power'
ATTR_TEMPERATURE = 'temperature'
ATTR_CURRENT = 'current'
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
            ATTR_TEMPERATURE: None,
            ATTR_CURRENT: None
        }

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
    def async_turn_on(self, **kwargs):
        """Turn the fan on."""

        result = yield from self._try_command(
            "Turning the air purifier on failed.", self._air_purifier.on)

        if result:
            self._state = True

    @asyncio.coroutine
    def async_turn_off(self, **kwargs):
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
                ATTR_CURRENT: state.current,
            }

        except DeviceException as ex:
            _LOGGER.error("Got exception while fetching the state: %s", ex)

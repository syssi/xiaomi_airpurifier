"""Support for Xiaomi Mi Air Purifier and Xiaomi Mi Air Humidifier."""
import asyncio
from enum import Enum
from functools import partial
import logging
from typing import Optional

from miio import (  # pylint: disable=import-error
    AirDogX3,
    AirDogX5,
    AirDogX7SM,
    AirFresh,
    AirFreshA1,
    AirFreshT2017,
    AirHumidifier,
    AirHumidifierJsq,
    AirHumidifierJsqs,
    AirHumidifierMiot,
    AirHumidifierMjjsq,
    AirPurifier,
    AirPurifierMiot,
    Device,
    DeviceException,
    Fan,
    Fan1C,
    FanLeshow,
    FanP5,
    FanP9,
    FanP10,
    FanP11,
)
from miio.airfresh import (  # pylint: disable=import-error, import-error
    LedBrightness as AirfreshLedBrightness,
    OperationMode as AirfreshOperationMode,
)
from miio.airfresh_t2017 import (  # pylint: disable=import-error, import-error
    DisplayOrientation as AirfreshT2017DisplayOrientation,
    OperationMode as AirfreshT2017OperationMode,
    PtcLevel as AirfreshT2017PtcLevel,
)
from miio.airhumidifier import (  # pylint: disable=import-error, import-error
    LedBrightness as AirhumidifierLedBrightness,
    OperationMode as AirhumidifierOperationMode,
)
from miio.airhumidifier_jsq import (  # pylint: disable=import-error, import-error
    LedBrightness as AirhumidifierJsqLedBrightness,
    OperationMode as AirhumidifierJsqOperationMode,
)
from miio.integrations.humidifier.deerma.airhumidifier_jsqs import (  # pylint: disable=import-error, import-error
    OperationMode as AirhumidifierJsqsOperationMode,
)
from miio.airhumidifier_miot import (  # pylint: disable=import-error, import-error
    LedBrightness as AirhumidifierMiotLedBrightness,
    OperationMode as AirhumidifierMiotOperationMode,
    PressedButton as AirhumidifierPressedButton,
)
from miio.airhumidifier_mjjsq import (  # pylint: disable=import-error, import-error
    OperationMode as AirhumidifierMjjsqOperationMode,
)
from miio.airpurifier import (  # pylint: disable=import-error, import-error
    LedBrightness as AirpurifierLedBrightness,
    OperationMode as AirpurifierOperationMode,
)
from miio.airpurifier_airdog import (  # pylint: disable=import-error, import-error
    OperationMode as AirDogOperationMode,
)
from miio.airpurifier_miot import (  # pylint: disable=import-error, import-error
    LedBrightness as AirpurifierMiotLedBrightness,
    OperationMode as AirpurifierMiotOperationMode,
)
from miio.fan_common import (  # pylint: disable=import-error, import-error
    LedBrightness as FanLedBrightness,
    MoveDirection as FanMoveDirection,
    OperationMode as FanOperationMode,
)
from miio.integrations.fan.leshow.fan_leshow import (  # pylint: disable=import-error, import-error
    OperationMode as FanLeshowOperationMode,
)
import voluptuous as vol

from homeassistant.components.fan import (
    ATTR_SPEED,
    PLATFORM_SCHEMA,
    SPEED_OFF,
    SUPPORT_DIRECTION,
    SUPPORT_OSCILLATE,
    SUPPORT_PRESET_MODE,
    SUPPORT_SET_SPEED,
    FanEntity,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_MODE,
    CONF_HOST,
    CONF_NAME,
    CONF_TOKEN,
)
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Xiaomi Miio Device"
DEFAULT_RETRIES = 20
DATA_KEY = "fan.xiaomi_miio_airpurifier"
DOMAIN = "xiaomi_miio_airpurifier"

CONF_MODEL = "model"
CONF_RETRIES = "retries"

MODEL_AIRPURIFIER_V1 = "zhimi.airpurifier.v1"
MODEL_AIRPURIFIER_V2 = "zhimi.airpurifier.v2"
MODEL_AIRPURIFIER_V3 = "zhimi.airpurifier.v3"
MODEL_AIRPURIFIER_V5 = "zhimi.airpurifier.v5"
MODEL_AIRPURIFIER_PRO = "zhimi.airpurifier.v6"
MODEL_AIRPURIFIER_PRO_V7 = "zhimi.airpurifier.v7"
MODEL_AIRPURIFIER_M1 = "zhimi.airpurifier.m1"
MODEL_AIRPURIFIER_M2 = "zhimi.airpurifier.m2"
MODEL_AIRPURIFIER_MA1 = "zhimi.airpurifier.ma1"
MODEL_AIRPURIFIER_MA2 = "zhimi.airpurifier.ma2"
MODEL_AIRPURIFIER_SA1 = "zhimi.airpurifier.sa1"
MODEL_AIRPURIFIER_SA2 = "zhimi.airpurifier.sa2"
MODEL_AIRPURIFIER_2S = "zhimi.airpurifier.mc1"
MODEL_AIRPURIFIER_2H = "zhimi.airpurifier.mc2"
MODEL_AIRPURIFIER_3 = "zhimi.airpurifier.ma4"
MODEL_AIRPURIFIER_3H = "zhimi.airpurifier.mb3"
MODEL_AIRPURIFIER_ZA1 = "zhimi.airpurifier.za1"
MODEL_AIRPURIFIER_AIRDOG_X3 = "airdog.airpurifier.x3"
MODEL_AIRPURIFIER_AIRDOG_X5 = "airdog.airpurifier.x5"
MODEL_AIRPURIFIER_AIRDOG_X7SM = "airdog.airpurifier.x7sm"

MODEL_AIRHUMIDIFIER_V1 = "zhimi.humidifier.v1"
MODEL_AIRHUMIDIFIER_CA1 = "zhimi.humidifier.ca1"
MODEL_AIRHUMIDIFIER_CA4 = "zhimi.humidifier.ca4"
MODEL_AIRHUMIDIFIER_CB1 = "zhimi.humidifier.cb1"
MODEL_AIRHUMIDIFIER_CB2 = "zhimi.humidifier.cb2"
MODEL_AIRHUMIDIFIER_MJJSQ = "deerma.humidifier.mjjsq"
MODEL_AIRHUMIDIFIER_JSQ = "deerma.humidifier.jsq"
MODEL_AIRHUMIDIFIER_JSQ1 = "deerma.humidifier.jsq1"
MODEL_AIRHUMIDIFIER_JSQ5 = "deerma.humidifier.jsq5"
MODEL_AIRHUMIDIFIER_JSQS = "deerma.humidifier.jsqs"
MODEL_AIRHUMIDIFIER_JSQ001 = "shuii.humidifier.jsq001"

MODEL_AIRFRESH_A1 = "dmaker.airfresh.a1"
MODEL_AIRFRESH_VA2 = "zhimi.airfresh.va2"
MODEL_AIRFRESH_VA4 = "zhimi.airfresh.va4"
MODEL_AIRFRESH_T2017 = "dmaker.airfresh.t2017"

MODEL_FAN_V2 = "zhimi.fan.v2"
MODEL_FAN_V3 = "zhimi.fan.v3"
MODEL_FAN_SA1 = "zhimi.fan.sa1"
MODEL_FAN_ZA1 = "zhimi.fan.za1"
MODEL_FAN_ZA3 = "zhimi.fan.za3"
MODEL_FAN_ZA4 = "zhimi.fan.za4"
MODEL_FAN_P5 = "dmaker.fan.p5"
MODEL_FAN_P8 = "dmaker.fan.p8"
MODEL_FAN_P9 = "dmaker.fan.p9"
MODEL_FAN_P10 = "dmaker.fan.p10"
MODEL_FAN_P11 = "dmaker.fan.p11"
MODEL_FAN_LESHOW_SS4 = "leshow.fan.ss4"
MODEL_FAN_1C = "dmaker.fan.1c"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_MODEL): vol.In(
            [
                MODEL_AIRPURIFIER_V1,
                MODEL_AIRPURIFIER_V2,
                MODEL_AIRPURIFIER_V3,
                MODEL_AIRPURIFIER_V5,
                MODEL_AIRPURIFIER_PRO,
                MODEL_AIRPURIFIER_PRO_V7,
                MODEL_AIRPURIFIER_M1,
                MODEL_AIRPURIFIER_M2,
                MODEL_AIRPURIFIER_MA1,
                MODEL_AIRPURIFIER_MA2,
                MODEL_AIRPURIFIER_SA1,
                MODEL_AIRPURIFIER_SA2,
                MODEL_AIRPURIFIER_2S,
                MODEL_AIRPURIFIER_2H,
                MODEL_AIRPURIFIER_3,
                MODEL_AIRPURIFIER_3H,
                MODEL_AIRPURIFIER_ZA1,
                MODEL_AIRPURIFIER_AIRDOG_X3,
                MODEL_AIRPURIFIER_AIRDOG_X5,
                MODEL_AIRPURIFIER_AIRDOG_X7SM,
                MODEL_AIRHUMIDIFIER_V1,
                MODEL_AIRHUMIDIFIER_CA1,
                MODEL_AIRHUMIDIFIER_CA4,
                MODEL_AIRHUMIDIFIER_CB1,
                MODEL_AIRHUMIDIFIER_CB2,
                MODEL_AIRHUMIDIFIER_MJJSQ,
                MODEL_AIRHUMIDIFIER_JSQ,
                MODEL_AIRHUMIDIFIER_JSQ1,
                MODEL_AIRHUMIDIFIER_JSQ5,
                MODEL_AIRHUMIDIFIER_JSQS,
                MODEL_AIRHUMIDIFIER_JSQ001,
                MODEL_AIRFRESH_A1,
                MODEL_AIRFRESH_VA2,
                MODEL_AIRFRESH_VA4,
                MODEL_AIRFRESH_T2017,
                MODEL_FAN_V2,
                MODEL_FAN_V3,
                MODEL_FAN_SA1,
                MODEL_FAN_ZA1,
                MODEL_FAN_ZA3,
                MODEL_FAN_ZA4,
                MODEL_FAN_P5,
                MODEL_FAN_P8,
                MODEL_FAN_P9,
                MODEL_FAN_P10,
                MODEL_FAN_P11,
                MODEL_FAN_LESHOW_SS4,
                MODEL_FAN_1C,
            ]
        ),
        vol.Optional(CONF_RETRIES, default=DEFAULT_RETRIES): cv.positive_int,
    }
)

ATTR_MODEL = "model"

# Air Purifier
ATTR_TEMPERATURE = "temperature"
ATTR_HUMIDITY = "humidity"
ATTR_AIR_QUALITY_INDEX = "aqi"
ATTR_FILTER_HOURS_USED = "filter_hours_used"
ATTR_FILTER_LIFE = "filter_life_remaining"
ATTR_FAVORITE_LEVEL = "favorite_level"
ATTR_BUZZER = "buzzer"
ATTR_CHILD_LOCK = "child_lock"
ATTR_LED = "led"
ATTR_LED_BRIGHTNESS = "led_brightness"
ATTR_MOTOR_SPEED = "motor_speed"
ATTR_AVERAGE_AIR_QUALITY_INDEX = "average_aqi"
ATTR_PURIFY_VOLUME = "purify_volume"
ATTR_BRIGHTNESS = "brightness"
ATTR_LEVEL = "level"
ATTR_FAN_LEVEL = "fan_level"
ATTR_MOTOR2_SPEED = "motor2_speed"
ATTR_ILLUMINANCE = "illuminance"
ATTR_FILTER_RFID_PRODUCT_ID = "filter_rfid_product_id"
ATTR_FILTER_RFID_TAG = "filter_rfid_tag"
ATTR_FILTER_TYPE = "filter_type"
ATTR_LEARN_MODE = "learn_mode"
ATTR_SLEEP_TIME = "sleep_time"
ATTR_SLEEP_LEARN_COUNT = "sleep_mode_learn_count"
ATTR_EXTRA_FEATURES = "extra_features"
ATTR_FEATURES = "features"
ATTR_TURBO_MODE_SUPPORTED = "turbo_mode_supported"
ATTR_AUTO_DETECT = "auto_detect"
ATTR_SLEEP_MODE = "sleep_mode"
ATTR_VOLUME = "volume"
ATTR_USE_TIME = "use_time"
ATTR_BUTTON_PRESSED = "button_pressed"

# Air Humidifier
ATTR_TARGET_HUMIDITY = "target_humidity"
ATTR_TRANS_LEVEL = "trans_level"
ATTR_HARDWARE_VERSION = "hardware_version"

# Air Humidifier CA
# ATTR_MOTOR_SPEED = "motor_speed"
ATTR_DEPTH = "depth"
ATTR_DRY = "dry"

# Air Humidifier CA4
ATTR_WATER_LEVEL = "water_level"
ATTR_ACTUAL_MOTOR_SPEED = "actual_speed"
ATTR_FAHRENHEIT = "fahrenheit"
ATTR_FAULT = "fault"
ATTR_POWER_TIME = "power_time"
ATTR_CLEAN_MODE = "clean_mode"

# Air Humidifier MJJSQ, JSQ, JSQ1, JSQ5 ans JSQS
ATTR_NO_WATER = "no_water"
ATTR_WATER_TANK_DETACHED = "water_tank_detached"
ATTR_WET_PROTECTION = "wet_protection"

# Air Humidifier JSQ001
ATTR_LID_OPENED = "lid_opened"

# Air Fresh
ATTR_CO2 = "co2"
ATTR_PTC = "ptc"

ATTR_NTC_TEMPERATURE = "ntc_temperature"

# Air Fresh T2017
ATTR_POWER = "power"
ATTR_PM25 = "pm25"
ATTR_FAVORITE_SPEED = "favorite_speed"
ATTR_CONTROL_SPEED = "control_speed"
ATTR_DUST_FILTER_LIFE_REMAINING = "dust_filter_life_remaining"
ATTR_DUST_FILTER_LIFE_REMAINING_DAYS = "dust_filter_life_remaining_days"
ATTR_UPPER_FILTER_LIFE_REMAINING = "upper_filter_life_remaining"
ATTR_UPPER_FILTER_LIFE_REMAINING_DAYS = "upper_filter_life_remaining_days"
ATTR_PTC_LEVEL = "ptc_level"
ATTR_PTC_STATUS = "ptc_status"
ATTR_DISPLAY = "display"
ATTR_DISPLAY_ORIENTATION = "display_orientation"

# Smart Fan
ATTR_NATURAL_SPEED = "natural_speed"
ATTR_OSCILLATE = "oscillate"
ATTR_BATTERY = "battery"
ATTR_BATTERY_CHARGE = "battery_charge"
ATTR_BATTERY_STATE = "battery_state"
ATTR_AC_POWER = "ac_power"
ATTR_DELAY_OFF_COUNTDOWN = "delay_off_countdown"
ATTR_ANGLE = "angle"
ATTR_DIRECT_SPEED = "direct_speed"
ATTR_SPEED_LEVEL = "speed_level"
ATTR_RAW_SPEED = "raw_speed"

# Fan Leshow SS4
ATTR_ERROR_DETECTED = "error_detected"

PURIFIER_MIOT = [MODEL_AIRPURIFIER_3, MODEL_AIRPURIFIER_3H, MODEL_AIRPURIFIER_ZA1]
HUMIDIFIER_MIOT = [MODEL_AIRHUMIDIFIER_CA4]

# AirDogX7SM
ATTR_FORMALDEHYDE = "hcho"
# AirDogX3, AirDogX5, AirDogX7SM
ATTR_CLEAN_FILTERS = "clean_filters"

# Map attributes to properties of the state object
AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_TURBO_MODE_SUPPORTED: "turbo_mode_supported",
    ATTR_BUTTON_PRESSED: "button_pressed",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_USE_TIME: "use_time",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_SLEEP_MODE: "sleep_mode",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_USE_TIME: "use_time",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_VOLUME: "volume",
    # perhaps supported but unconfirmed
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO_V7 = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_VOLUME: "volume",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_2S = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_COMMON,
    ATTR_BUZZER: "buzzer",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_ILLUMINANCE: "illuminance",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_2H = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_TURBO_MODE_SUPPORTED: "turbo_mode_supported",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_3 = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FAVORITE_LEVEL: "favorite_level",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_USE_TIME: "use_time",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_FAN_LEVEL: "fan_level",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_V3 = {
    # Common set isn't used here. It's a very basic version of the device.
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_MODE: "mode",
    ATTR_LED: "led",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_ILLUMINANCE: "illuminance",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_MOTOR_SPEED: "motor_speed",
    # perhaps supported but unconfirmed
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_VOLUME: "volume",
    ATTR_MOTOR2_SPEED: "motor2_speed",
    ATTR_FILTER_RFID_PRODUCT_ID: "filter_rfid_product_id",
    ATTR_FILTER_RFID_TAG: "filter_rfid_tag",
    ATTR_FILTER_TYPE: "filter_type",
    ATTR_PURIFY_VOLUME: "purify_volume",
    ATTR_LEARN_MODE: "learn_mode",
    ATTR_SLEEP_TIME: "sleep_time",
    ATTR_SLEEP_LEARN_COUNT: "sleep_mode_learn_count",
    ATTR_EXTRA_FEATURES: "extra_features",
    ATTR_AUTO_DETECT: "auto_detect",
    ATTR_USE_TIME: "use_time",
    ATTR_BUTTON_PRESSED: "button_pressed",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_MODE: "mode",
    ATTR_BUZZER: "buzzer",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_TRANS_LEVEL: "trans_level",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
    ATTR_HARDWARE_VERSION: "hardware_version",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_DEPTH: "depth",  # deprecated
    ATTR_DRY: "dry",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
    ATTR_HARDWARE_VERSION: "hardware_version",
    ATTR_WATER_LEVEL: "water_level",
    ATTR_WATER_TANK_DETACHED: "water_tank_detached",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4 = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_ACTUAL_MOTOR_SPEED: "actual_speed",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_DRY: "dry",
    ATTR_FAHRENHEIT: "fahrenheit",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_POWER_TIME: "power_time",
    ATTR_WATER_LEVEL: "water_level",
    ATTR_USE_TIME: "use_time",
    ATTR_CLEAN_MODE: "clean_mode",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_LED: "led",
    ATTR_NO_WATER: "no_water",
    ATTR_WATER_TANK_DETACHED: "water_tank_detached",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1 = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ,
    ATTR_WET_PROTECTION: "wet_protection",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5 = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_HUMIDITY: "relative_humidity",
    ATTR_TARGET_HUMIDITY: "target_humidity",
    ATTR_LED: "led_light",
    ATTR_NO_WATER: "water_shortage_fault",
    ATTR_WATER_TANK_DETACHED: "tank_filed",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5,
    ATTR_WET_PROTECTION: "overwet_protect",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED: "led",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_NO_WATER: "no_water",
    ATTR_LID_OPENED: "lid_opened",
}

AVAILABLE_ATTRIBUTES_AIRFRESH = {
    ATTR_TEMPERATURE: "temperature",
    ATTR_AIR_QUALITY_INDEX: "aqi",
    ATTR_AVERAGE_AIR_QUALITY_INDEX: "average_aqi",
    ATTR_CO2: "co2",
    ATTR_HUMIDITY: "humidity",
    ATTR_MODE: "mode",
    ATTR_LED: "led",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_FILTER_LIFE: "filter_life_remaining",
    ATTR_FILTER_HOURS_USED: "filter_hours_used",
    ATTR_USE_TIME: "use_time",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_EXTRA_FEATURES: "extra_features",
}

AVAILABLE_ATTRIBUTES_AIRFRESH_VA4 = {
    **AVAILABLE_ATTRIBUTES_AIRFRESH,
    ATTR_PTC: "ptc",
    ATTR_NTC_TEMPERATURE: "ntc_temperature",
}

AVAILABLE_ATTRIBUTES_AIRFRESH_A1 = {
    ATTR_POWER: "power",
    ATTR_MODE: "mode",
    ATTR_PM25: "pm25",
    ATTR_CO2: "co2",
    ATTR_TEMPERATURE: "temperature",
    ATTR_FAVORITE_SPEED: "favorite_speed",
    ATTR_CONTROL_SPEED: "control_speed",
    ATTR_DUST_FILTER_LIFE_REMAINING: "dust_filter_life_remaining",
    ATTR_DUST_FILTER_LIFE_REMAINING_DAYS: "dust_filter_life_remaining_days",
    ATTR_PTC: "ptc",
    ATTR_PTC_STATUS: "ptc_status",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_BUZZER: "buzzer",
    ATTR_DISPLAY: "display",
}

AVAILABLE_ATTRIBUTES_AIRFRESH_T2017 = {
    **AVAILABLE_ATTRIBUTES_AIRFRESH_A1,
    ATTR_UPPER_FILTER_LIFE_REMAINING: "upper_filter_life_remaining",
    ATTR_UPPER_FILTER_LIFE_REMAINING_DAYS: "upper_filter_life_remaining_days",
    ATTR_PTC_LEVEL: "ptc_level",
    ATTR_DISPLAY_ORIENTATION: "display_orientation",
}

AVAILABLE_ATTRIBUTES_FAN = {
    ATTR_ANGLE: "angle",
    ATTR_RAW_SPEED: "speed",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_AC_POWER: "ac_power",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DIRECT_SPEED: "direct_speed",
    ATTR_NATURAL_SPEED: "natural_speed",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_BUZZER: "buzzer",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
    # Additional properties of version 2 and 3
    ATTR_TEMPERATURE: "temperature",
    ATTR_HUMIDITY: "humidity",
    ATTR_BATTERY: "battery",
    ATTR_BATTERY_CHARGE: "battery_charge",
    ATTR_BUTTON_PRESSED: "button_pressed",
    # Additional properties of version 2
    ATTR_LED: "led",
    ATTR_BATTERY_STATE: "battery_state",
}

AVAILABLE_ATTRIBUTES_FAN_P5 = {
    ATTR_MODE: "mode",
    ATTR_OSCILLATE: "oscillate",
    ATTR_ANGLE: "angle",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_LED: "led",
    ATTR_BUZZER: "buzzer",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_RAW_SPEED: "speed",
}

AVAILABLE_ATTRIBUTES_FAN_LESHOW_SS4 = {
    ATTR_MODE: "mode",
    ATTR_RAW_SPEED: "speed",
    ATTR_BUZZER: "buzzer",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_ERROR_DETECTED: "error_detected",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3 = {
    ATTR_MODE: "mode",
    ATTR_SPEED: "speed",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_CLEAN_FILTERS: "clean_filters",
    ATTR_PM25: "pm25",
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X5 = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3,
}

AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X7SM = {
    **AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3,
    ATTR_FORMALDEHYDE: "hcho",
}

AVAILABLE_ATTRIBUTES_FAN_1C = {
    ATTR_MODE: "mode",
    ATTR_RAW_SPEED: "speed",
    ATTR_BUZZER: "buzzer",
    ATTR_OSCILLATE: "oscillate",
    ATTR_DELAY_OFF_COUNTDOWN: "delay_off_countdown",
    ATTR_LED: "led",
    ATTR_CHILD_LOCK: "child_lock",
}

FAN_SPEED_LEVEL1 = "Level 1"
FAN_SPEED_LEVEL2 = "Level 2"
FAN_SPEED_LEVEL3 = "Level 3"
FAN_SPEED_LEVEL4 = "Level 4"

FAN_PRESET_MODES = {
    SPEED_OFF: range(0, 1),
    FAN_SPEED_LEVEL1: range(1, 26),
    FAN_SPEED_LEVEL2: range(26, 51),
    FAN_SPEED_LEVEL3: range(51, 76),
    FAN_SPEED_LEVEL4: range(76, 101),
}

FAN_PRESET_MODE_VALUES = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 74,
    FAN_SPEED_LEVEL4: 100,
}

FAN_PRESET_MODE_VALUES_P5 = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 70,
    FAN_SPEED_LEVEL4: 100,
}

FAN_PRESET_MODES_1C = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 2,
    FAN_SPEED_LEVEL3: 3,
}

FAN_SPEEDS_1C = list(FAN_PRESET_MODES_1C)
FAN_SPEEDS_1C.remove(SPEED_OFF)

OPERATION_MODES_AIRPURIFIER = ["Auto", "Silent", "Favorite", "Idle"]
OPERATION_MODES_AIRPURIFIER_PRO = ["Auto", "Silent", "Favorite"]
OPERATION_MODES_AIRPURIFIER_PRO_V7 = OPERATION_MODES_AIRPURIFIER_PRO
OPERATION_MODES_AIRPURIFIER_2S = ["Auto", "Silent", "Favorite"]
OPERATION_MODES_AIRPURIFIER_2H = OPERATION_MODES_AIRPURIFIER
OPERATION_MODES_AIRPURIFIER_3 = ["Auto", "Silent", "Favorite", "Fan"]
OPERATION_MODES_AIRPURIFIER_V3 = [
    "Auto",
    "Silent",
    "Favorite",
    "Idle",
    "Medium",
    "High",
    "Strong",
]
OPERATION_MODES_AIRFRESH = ["Auto", "Silent", "Interval", "Low", "Middle", "Strong"]
OPERATION_MODES_AIRFRESH_T2017 = ["Auto", "Sleep", "Favorite"]

SUCCESS = ["ok"]

FEATURE_SET_BUZZER = 1
FEATURE_SET_LED = 2
FEATURE_SET_CHILD_LOCK = 4
FEATURE_SET_LED_BRIGHTNESS = 8
FEATURE_SET_FAVORITE_LEVEL = 16
FEATURE_SET_AUTO_DETECT = 32
FEATURE_SET_LEARN_MODE = 64
FEATURE_SET_VOLUME = 128
FEATURE_RESET_FILTER = 256
FEATURE_SET_EXTRA_FEATURES = 512
FEATURE_SET_TARGET_HUMIDITY = 1024
FEATURE_SET_DRY = 2048
FEATURE_SET_FAN_LEVEL = 16384
FEATURE_SET_MOTOR_SPEED = 32768
FEATURE_SET_PTC_LEVEL = 131072
FEATURE_SET_FAVORITE_SPEED = 262144
FEATURE_SET_DISPLAY_ORIENTATION = 524288
FEATURE_SET_WET_PROTECTION = 1048576
FEATURE_SET_CLEAN_MODE = 2097152

# Smart Fan
FEATURE_SET_OSCILLATION_ANGLE = 4096
FEATURE_SET_NATURAL_MODE = 8192

# Airfresh VA4
FEATURE_SET_PTC = 65536

FEATURE_FLAGS_AIRPURIFIER = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_LEARN_MODE
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
)

FEATURE_FLAGS_AIRPURIFIER_PRO = (
    FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_AUTO_DETECT
    | FEATURE_SET_VOLUME
)

FEATURE_FLAGS_AIRPURIFIER_PRO_V7 = (
    FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_VOLUME
)

FEATURE_FLAGS_AIRPURIFIER_2S = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
)

FEATURE_FLAGS_AIRPURIFIER_2H = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_LED_BRIGHTNESS
)

FEATURE_FLAGS_AIRPURIFIER_3 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_FAVORITE_LEVEL
    | FEATURE_SET_FAN_LEVEL
    | FEATURE_SET_LED_BRIGHTNESS
)

FEATURE_FLAGS_AIRPURIFIER_V3 = (
    FEATURE_SET_BUZZER | FEATURE_SET_CHILD_LOCK | FEATURE_SET_LED
)

FEATURE_FLAGS_AIRHUMIDIFIER = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB = FEATURE_FLAGS_AIRHUMIDIFIER | FEATURE_SET_DRY

FEATURE_FLAGS_AIRHUMIDIFIER_CA4 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_TARGET_HUMIDITY
    | FEATURE_SET_DRY
    | FEATURE_SET_MOTOR_SPEED
    | FEATURE_SET_CLEAN_MODE
)

FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ = (
    FEATURE_SET_BUZZER | FEATURE_SET_LED | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_LED
    | FEATURE_SET_TARGET_HUMIDITY
    | FEATURE_SET_WET_PROTECTION
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5 = (
    FEATURE_SET_BUZZER | FEATURE_SET_LED | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQS = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_LED
    | FEATURE_SET_TARGET_HUMIDITY
    | FEATURE_SET_WET_PROTECTION
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQ = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_CHILD_LOCK
)

FEATURE_FLAGS_AIRFRESH = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
)

FEATURE_FLAGS_AIRFRESH_VA4 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_RESET_FILTER
    | FEATURE_SET_EXTRA_FEATURES
    | FEATURE_SET_PTC
)

FEATURE_FLAGS_AIRFRESH_A1 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_RESET_FILTER
    | FEATURE_SET_PTC
    | FEATURE_SET_FAVORITE_SPEED
)

FEATURE_FLAGS_AIRFRESH_T2017 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED
    | FEATURE_RESET_FILTER
    | FEATURE_SET_PTC
    | FEATURE_SET_PTC_LEVEL
    | FEATURE_SET_FAVORITE_SPEED
    | FEATURE_SET_DISPLAY_ORIENTATION
)

FEATURE_FLAGS_FAN = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_LED_BRIGHTNESS
    | FEATURE_SET_OSCILLATION_ANGLE
    | FEATURE_SET_NATURAL_MODE
)

FEATURE_FLAGS_FAN_P5 = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_CHILD_LOCK
    | FEATURE_SET_NATURAL_MODE
    | FEATURE_SET_OSCILLATION_ANGLE
    | FEATURE_SET_LED
)

FEATURE_FLAGS_FAN_LESHOW_SS4 = FEATURE_SET_BUZZER
FEATURE_FLAGS_FAN_1C = FEATURE_FLAGS_FAN

FEATURE_FLAGS_AIRPURIFIER_AIRDOG = FEATURE_SET_CHILD_LOCK

SERVICE_SET_BUZZER_ON = "fan_set_buzzer_on"
SERVICE_SET_BUZZER_OFF = "fan_set_buzzer_off"
SERVICE_SET_FAN_LED_ON = "fan_set_led_on"
SERVICE_SET_FAN_LED_OFF = "fan_set_led_off"
SERVICE_SET_CHILD_LOCK_ON = "fan_set_child_lock_on"
SERVICE_SET_CHILD_LOCK_OFF = "fan_set_child_lock_off"
SERVICE_SET_LED_BRIGHTNESS = "fan_set_led_brightness"
SERVICE_SET_FAVORITE_LEVEL = "fan_set_favorite_level"
SERVICE_SET_FAN_LEVEL = "fan_set_fan_level"
SERVICE_SET_AUTO_DETECT_ON = "fan_set_auto_detect_on"
SERVICE_SET_AUTO_DETECT_OFF = "fan_set_auto_detect_off"
SERVICE_SET_LEARN_MODE_ON = "fan_set_learn_mode_on"
SERVICE_SET_LEARN_MODE_OFF = "fan_set_learn_mode_off"
SERVICE_SET_MOTOR_SPEED = "fan_set_motor_speed"
SERVICE_SET_VOLUME = "fan_set_volume"
SERVICE_RESET_FILTER = "fan_reset_filter"
SERVICE_SET_EXTRA_FEATURES = "fan_set_extra_features"
SERVICE_SET_TARGET_HUMIDITY = "fan_set_target_humidity"
SERVICE_SET_DRY_ON = "fan_set_dry_on"
SERVICE_SET_DRY_OFF = "fan_set_dry_off"
SERVICE_SET_FILTERS_CLEANED = "fan_set_filters_cleaned"

# Airhumidifer CA4
SERVICE_SET_CLEAN_MODE_ON = "fan_set_clean_mode_on"
SERVICE_SET_CLEAN_MODE_OFF = "fan_set_clean_mode_off"

# Airhumidifer JSQ1
SERVICE_SET_WET_PROTECTION_ON = "fan_set_wet_protection_on"
SERVICE_SET_WET_PROTECTION_OFF = "fan_set_wet_protection_off"

# Airfresh T2017
SERVICE_SET_FAVORITE_SPEED = "fan_set_favorite_speed"
SERVICE_SET_DISPLAY_ON = "fan_set_display_on"
SERVICE_SET_DISPLAY_OFF = "fan_set_display_off"
SERVICE_SET_PTC_LEVEL = "fan_set_ptc_level"
SERVICE_SET_DISPLAY_ORIENTATION = "fan_set_display_orientation"

# Smart Fan
SERVICE_SET_DELAY_OFF = "fan_set_delay_off"
SERVICE_SET_OSCILLATION_ANGLE = "fan_set_oscillation_angle"
SERVICE_SET_NATURAL_MODE_ON = "fan_set_natural_mode_on"
SERVICE_SET_NATURAL_MODE_OFF = "fan_set_natural_mode_off"

# Airfresh VA4
SERVICE_SET_PTC_ON = "fan_set_ptc_on"
SERVICE_SET_PTC_OFF = "fan_set_ptc_off"

AIRPURIFIER_SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTITY_ID): cv.entity_ids})

SERVICE_SCHEMA_LED_BRIGHTNESS = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_BRIGHTNESS): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=2))}
)

SERVICE_SCHEMA_FAVORITE_LEVEL = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_LEVEL): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=17))}
)

SERVICE_SCHEMA_FAN_LEVEL = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_LEVEL): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=3))}
)

SERVICE_SCHEMA_VOLUME = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_VOLUME): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=100))}
)

SERVICE_SCHEMA_EXTRA_FEATURES = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_FEATURES): cv.positive_int}
)

SERVICE_SCHEMA_TARGET_HUMIDITY = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_HUMIDITY): vol.All(vol.Coerce(int), vol.Clamp(min=0, max=99))}
)

SERVICE_SCHEMA_FAVORITE_SPEED = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_SPEED): vol.All(vol.Coerce(int), vol.Clamp(min=60, max=300))}
)

SERVICE_SCHEMA_PTC_LEVEL = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_LEVEL): vol.In([level.name for level in AirfreshT2017PtcLevel])}
)

SERVICE_SCHEMA_DISPLAY_ORIENTATION = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_DISPLAY_ORIENTATION): vol.In(
            [orientation.name for orientation in AirfreshT2017DisplayOrientation]
        )
    }
)

SERVICE_SCHEMA_MOTOR_SPEED = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_MOTOR_SPEED): vol.All(
            vol.Coerce(int), vol.Clamp(min=200, max=2000)
        )
    }
)

SERVICE_SCHEMA_OSCILLATION_ANGLE = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_ANGLE): cv.positive_int}
)

SERVICE_SCHEMA_DELAY_OFF = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_DELAY_OFF_COUNTDOWN): vol.All(
            vol.Coerce(int), vol.In([0, 60, 120, 180, 240, 300, 360, 420, 480])
        )
    }
)

SERVICE_TO_METHOD = {
    SERVICE_SET_BUZZER_ON: {"method": "async_set_buzzer_on"},
    SERVICE_SET_BUZZER_OFF: {"method": "async_set_buzzer_off"},
    SERVICE_SET_FAN_LED_ON: {"method": "async_set_led_on"},
    SERVICE_SET_FAN_LED_OFF: {"method": "async_set_led_off"},
    SERVICE_SET_CHILD_LOCK_ON: {"method": "async_set_child_lock_on"},
    SERVICE_SET_CHILD_LOCK_OFF: {"method": "async_set_child_lock_off"},
    SERVICE_SET_AUTO_DETECT_ON: {"method": "async_set_auto_detect_on"},
    SERVICE_SET_AUTO_DETECT_OFF: {"method": "async_set_auto_detect_off"},
    SERVICE_SET_LEARN_MODE_ON: {"method": "async_set_learn_mode_on"},
    SERVICE_SET_LEARN_MODE_OFF: {"method": "async_set_learn_mode_off"},
    SERVICE_RESET_FILTER: {"method": "async_reset_filter"},
    SERVICE_SET_LED_BRIGHTNESS: {
        "method": "async_set_led_brightness",
        "schema": SERVICE_SCHEMA_LED_BRIGHTNESS,
    },
    SERVICE_SET_FAVORITE_LEVEL: {
        "method": "async_set_favorite_level",
        "schema": SERVICE_SCHEMA_FAVORITE_LEVEL,
    },
    SERVICE_SET_FAVORITE_SPEED: {
        "method": "async_set_favorite_speed",
        "schema": SERVICE_SCHEMA_FAVORITE_SPEED,
    },
    SERVICE_SET_FAN_LEVEL: {
        "method": "async_set_fan_level",
        "schema": SERVICE_SCHEMA_FAN_LEVEL,
    },
    SERVICE_SET_VOLUME: {"method": "async_set_volume", "schema": SERVICE_SCHEMA_VOLUME},
    SERVICE_SET_EXTRA_FEATURES: {
        "method": "async_set_extra_features",
        "schema": SERVICE_SCHEMA_EXTRA_FEATURES,
    },
    SERVICE_SET_TARGET_HUMIDITY: {
        "method": "async_set_target_humidity",
        "schema": SERVICE_SCHEMA_TARGET_HUMIDITY,
    },
    SERVICE_SET_MOTOR_SPEED: {
        "method": "async_set_motor_speed",
        "schema": SERVICE_SCHEMA_MOTOR_SPEED,
    },
    SERVICE_SET_DRY_ON: {"method": "async_set_dry_on"},
    SERVICE_SET_DRY_OFF: {"method": "async_set_dry_off"},
    SERVICE_SET_OSCILLATION_ANGLE: {
        "method": "async_set_oscillation_angle",
        "schema": SERVICE_SCHEMA_OSCILLATION_ANGLE,
    },
    SERVICE_SET_DELAY_OFF: {
        "method": "async_set_delay_off",
        "schema": SERVICE_SCHEMA_DELAY_OFF,
    },
    SERVICE_SET_NATURAL_MODE_ON: {"method": "async_set_natural_mode_on"},
    SERVICE_SET_NATURAL_MODE_OFF: {"method": "async_set_natural_mode_off"},
    SERVICE_SET_PTC_LEVEL: {
        "method": "async_set_ptc_level",
        "schema": SERVICE_SCHEMA_PTC_LEVEL,
    },
    SERVICE_SET_DISPLAY_ORIENTATION: {
        "method": "async_set_display_orientation",
        "schema": SERVICE_SCHEMA_DISPLAY_ORIENTATION,
    },
    SERVICE_SET_PTC_ON: {"method": "async_set_ptc_on"},
    SERVICE_SET_PTC_OFF: {"method": "async_set_ptc_off"},
    SERVICE_SET_DISPLAY_ON: {"method": "async_set_display_on"},
    SERVICE_SET_DISPLAY_OFF: {"method": "async_set_display_off"},
    SERVICE_SET_WET_PROTECTION_ON: {"method": "async_set_wet_protection_on"},
    SERVICE_SET_WET_PROTECTION_OFF: {"method": "async_set_wet_protection_off"},
    SERVICE_SET_CLEAN_MODE_ON: {"method": "async_set_clean_mode_on"},
    SERVICE_SET_CLEAN_MODE_OFF: {"method": "async_set_clean_mode_off"},
    SERVICE_SET_FILTERS_CLEANED: {"method": "async_set_filters_cleaned"},
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the miio fan device from config."""
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config[CONF_NAME]
    model = config.get(CONF_MODEL)
    retries = config[CONF_RETRIES]

    _LOGGER.info("Initializing with host %s (token %s...)", host, token[:5])
    unique_id = None

    if model is None:
        try:
            miio_device = Device(host, token)
            device_info = await hass.async_add_executor_job(miio_device.info)
            model = device_info.model
            unique_id = f"{model}-{device_info.mac_address}"
            _LOGGER.info(
                "%s %s %s detected",
                model,
                device_info.firmware_version,
                device_info.hardware_version,
            )
        except DeviceException as ex:
            raise PlatformNotReady from ex

    if model in PURIFIER_MIOT:
        air_purifier = AirPurifierMiot(host, token)
        device = XiaomiAirPurifierMiot(name, air_purifier, model, unique_id, retries)
    elif model.startswith("zhimi.airpurifier."):
        air_purifier = AirPurifier(host, token)
        device = XiaomiAirPurifier(name, air_purifier, model, unique_id)
    elif model in HUMIDIFIER_MIOT:
        air_humidifier = AirHumidifierMiot(host, token)
        device = XiaomiAirHumidifierMiot(name, air_humidifier, model, unique_id)
    elif model.startswith("zhimi.humidifier."):
        air_humidifier = AirHumidifier(host, token, model=model)
        device = XiaomiAirHumidifier(name, air_humidifier, model, unique_id)
    elif model in [
        MODEL_AIRHUMIDIFIER_MJJSQ,
        MODEL_AIRHUMIDIFIER_JSQ,
        MODEL_AIRHUMIDIFIER_JSQ1,
    ]:
        air_humidifier = AirHumidifierMjjsq(host, token, model=model)
        device = XiaomiAirHumidifierMjjsq(name, air_humidifier, model, unique_id)
    elif model in [
        MODEL_AIRHUMIDIFIER_JSQ5,
        MODEL_AIRHUMIDIFIER_JSQS,
    ]:
        air_humidifier = AirHumidifierJsqs(host, token, model=model)
        device = XiaomiAirHumidifierJsqs(name, air_humidifier, model, unique_id)
    elif model == MODEL_AIRHUMIDIFIER_JSQ001:
        air_humidifier = AirHumidifierJsq(host, token, model=model)
        device = XiaomiAirHumidifierJsq(name, air_humidifier, model, unique_id)
    elif model.startswith("zhimi.airfresh."):
        air_fresh = AirFresh(host, token, model=model)
        device = XiaomiAirFresh(name, air_fresh, model, unique_id)
    elif model == MODEL_AIRFRESH_A1:
        air_fresh = AirFreshA1(host, token, model=model)
        device = XiaomiAirFreshA1(name, air_fresh, model, unique_id)
    elif model == MODEL_AIRFRESH_T2017:
        air_fresh = AirFreshT2017(host, token, model=model)
        device = XiaomiAirFreshT2017(name, air_fresh, model, unique_id)
    elif model in [
        MODEL_FAN_V2,
        MODEL_FAN_V3,
        MODEL_FAN_SA1,
        MODEL_FAN_ZA1,
        MODEL_FAN_ZA3,
        MODEL_FAN_ZA4,
    ]:
        fan = Fan(host, token, model=model)
        device = XiaomiFan(name, fan, model, unique_id, retries)
    elif model == MODEL_FAN_P5:
        fan = FanP5(host, token, model=model)
        device = XiaomiFanP5(name, fan, model, unique_id, retries)
    elif model == MODEL_FAN_P9:
        fan = FanP9(host, token, model=model)
        device = XiaomiFanMiot(name, fan, model, unique_id, retries)
    elif model == MODEL_FAN_P10:
        fan = FanP10(host, token, model=model)
        device = XiaomiFanMiot(name, fan, model, unique_id, retries)
    elif model == MODEL_FAN_P11:
        fan = FanP11(host, token, model=model)
        device = XiaomiFanMiot(name, fan, model, unique_id, retries)
    elif model == MODEL_FAN_LESHOW_SS4:
        fan = FanLeshow(host, token, model=model)
        device = XiaomiFanLeshow(name, fan, model, unique_id, retries)
    elif model == MODEL_AIRPURIFIER_AIRDOG_X3:
        air_purifier = AirDogX3(host, token)
        device = XiaomiAirDog(name, air_purifier, model, unique_id, retries)
    elif model == MODEL_AIRPURIFIER_AIRDOG_X5:
        air_purifier = AirDogX5(host, token)
        device = XiaomiAirDog(name, air_purifier, model, unique_id, retries)
    elif model == MODEL_AIRPURIFIER_AIRDOG_X7SM:
        air_purifier = AirDogX7SM(host, token)
        device = XiaomiAirDog(name, air_purifier, model, unique_id, retries)
    elif model in [MODEL_FAN_1C, MODEL_FAN_P8]:
        fan = Fan1C(host, token, model=model)
        device = XiaomiFan1C(name, fan, model, unique_id, retries)
    else:
        _LOGGER.error(
            "Unsupported device found! Please create an issue at "
            "https://github.com/syssi/xiaomi_airpurifier/issues "
            "and provide the following data: %s",
            model,
        )
        return False

    hass.data[DATA_KEY][host] = device
    async_add_entities([device], update_before_add=True)

    async def async_service_handler(service):
        """Map services to methods on XiaomiAirPurifier."""
        method = SERVICE_TO_METHOD.get(service.service)
        params = {
            key: value for key, value in service.data.items() if key != ATTR_ENTITY_ID
        }
        entity_ids = service.data.get(ATTR_ENTITY_ID)
        if entity_ids:
            devices = [
                device
                for device in hass.data[DATA_KEY].values()
                if device.entity_id in entity_ids
            ]
        else:
            devices = hass.data[DATA_KEY].values()

        update_tasks = []
        for device in devices:
            if not hasattr(device, method["method"]):
                continue
            await getattr(device, method["method"])(**params)
            update_tasks.append(device.async_update_ha_state(True))

        if update_tasks:
            await asyncio.wait(update_tasks)

    for air_purifier_service in SERVICE_TO_METHOD:
        schema = SERVICE_TO_METHOD[air_purifier_service].get(
            "schema", AIRPURIFIER_SERVICE_SCHEMA
        )
        hass.services.async_register(
            DOMAIN, air_purifier_service, async_service_handler, schema=schema
        )


class XiaomiGenericDevice(FanEntity):
    """Representation of a generic Xiaomi device."""

    def __init__(self, name, device, model, unique_id, retries=0):
        """Initialize the generic Xiaomi device."""
        self._name = name
        self._device = device
        self._model = model
        self._unique_id = unique_id
        self._retry = 0
        self._retries = retries

        self._available = False
        self._state = None
        self._state_attrs = {ATTR_MODEL: self._model}
        self._device_features = FEATURE_SET_CHILD_LOCK
        self._skip_update = False

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_PRESET_MODE

    @property
    def should_poll(self):
        """Poll the device."""
        return True

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes of the device."""
        return self._state_attrs

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    @staticmethod
    def _extract_value_from_attribute(state, attribute):
        value = getattr(state, attribute)
        if isinstance(value, Enum):
            return value.value

        return value

    async def _try_command(self, mask_error, func, *args, **kwargs):
        """Call a miio device command handling error messages."""
        try:
            result = await self.hass.async_add_executor_job(
                partial(func, *args, **kwargs)
            )

            _LOGGER.debug("Response received from miio device: %s", result)

            return result == SUCCESS
        except DeviceException as exc:
            _LOGGER.error(mask_error, exc)
            self._available = False
            return False

    async def async_turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:
        """Turn the device on."""
        if preset_mode:
            # If operation mode was set the device must not be turned on.
            result = await self.async_set_preset_mode(preset_mode)
        else:
            result = await self._try_command(
                "Turning the miio device on failed.", self._device.on
            )

        if result:
            self._state = True
            self._skip_update = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the device off."""
        result = await self._try_command(
            "Turning the miio device off failed.", self._device.off
        )

        if result:
            self._state = False
            self._skip_update = True

    async def async_set_buzzer_on(self):
        """Turn the buzzer on."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return

        await self._try_command(
            "Turning the buzzer of the miio device on failed.",
            self._device.set_buzzer,
            True,
        )

    async def async_set_buzzer_off(self):
        """Turn the buzzer off."""
        if self._device_features & FEATURE_SET_BUZZER == 0:
            return

        await self._try_command(
            "Turning the buzzer of the miio device off failed.",
            self._device.set_buzzer,
            False,
        )

    async def async_set_child_lock_on(self):
        """Turn the child lock on."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return

        await self._try_command(
            "Turning the child lock of the miio device on failed.",
            self._device.set_child_lock,
            True,
        )

    async def async_set_child_lock_off(self):
        """Turn the child lock off."""
        if self._device_features & FEATURE_SET_CHILD_LOCK == 0:
            return

        await self._try_command(
            "Turning the child lock of the miio device off failed.",
            self._device.set_child_lock,
            False,
        )


class XiaomiAirPurifier(XiaomiGenericDevice):
    """Representation of a Xiaomi Air Purifier."""

    def __init__(self, name, device, model, unique_id, retries=0):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id, retries)

        if self._model == MODEL_AIRPURIFIER_PRO:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_PRO
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO
            self._preset_modes = OPERATION_MODES_AIRPURIFIER_PRO
        elif self._model == MODEL_AIRPURIFIER_PRO_V7:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_PRO_V7
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO_V7
            self._preset_modes = OPERATION_MODES_AIRPURIFIER_PRO_V7
        elif self._model == MODEL_AIRPURIFIER_2S:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_2S
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_2S
            self._preset_modes = OPERATION_MODES_AIRPURIFIER_2S
        elif self._model == MODEL_AIRPURIFIER_2H:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_2H
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_2H
            self._preset_modes = OPERATION_MODES_AIRPURIFIER_2H
        elif self._model in PURIFIER_MIOT:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_3
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_3
            self._preset_modes = OPERATION_MODES_AIRPURIFIER_3
        elif self._model == MODEL_AIRPURIFIER_V3:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_V3
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_V3
            self._preset_modes = OPERATION_MODES_AIRPURIFIER_V3
        else:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER
            self._preset_modes = OPERATION_MODES_AIRPURIFIER

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._state = state.is_on
            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )

            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirpurifierOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirpurifierOperationMode[preset_mode.title()],
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device on failed.", self._device.set_led, True
        )

    async def async_set_led_off(self):
        """Turn the led off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_led,
            False,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirpurifierLedBrightness(brightness),
        )

    async def async_set_favorite_level(self, level: int = 1):
        """Set the favorite level."""
        if self._device_features & FEATURE_SET_FAVORITE_LEVEL == 0:
            return

        await self._try_command(
            "Setting the favorite level of the miio device failed.",
            self._device.set_favorite_level,
            level,
        )

    async def async_set_fan_level(self, level: int = 1):
        """Set the favorite level."""
        if self._device_features & FEATURE_SET_FAN_LEVEL == 0:
            return

        await self._try_command(
            "Setting the fan level of the miio device failed.",
            self._device.set_fan_level,
            level,
        )

    async def async_set_auto_detect_on(self):
        """Turn the auto detect on."""
        if self._device_features & FEATURE_SET_AUTO_DETECT == 0:
            return

        await self._try_command(
            "Turning the auto detect of the miio device on failed.",
            self._device.set_auto_detect,
            True,
        )

    async def async_set_auto_detect_off(self):
        """Turn the auto detect off."""
        if self._device_features & FEATURE_SET_AUTO_DETECT == 0:
            return

        await self._try_command(
            "Turning the auto detect of the miio device off failed.",
            self._device.set_auto_detect,
            False,
        )

    async def async_set_learn_mode_on(self):
        """Turn the learn mode on."""
        if self._device_features & FEATURE_SET_LEARN_MODE == 0:
            return

        await self._try_command(
            "Turning the learn mode of the miio device on failed.",
            self._device.set_learn_mode,
            True,
        )

    async def async_set_learn_mode_off(self):
        """Turn the learn mode off."""
        if self._device_features & FEATURE_SET_LEARN_MODE == 0:
            return

        await self._try_command(
            "Turning the learn mode of the miio device off failed.",
            self._device.set_learn_mode,
            False,
        )

    async def async_set_volume(self, volume: int = 50):
        """Set the sound volume."""
        if self._device_features & FEATURE_SET_VOLUME == 0:
            return

        await self._try_command(
            "Setting the sound volume of the miio device failed.",
            self._device.set_volume,
            volume,
        )

    async def async_set_extra_features(self, features: int = 1):
        """Set the extra features."""
        if self._device_features & FEATURE_SET_EXTRA_FEATURES == 0:
            return

        await self._try_command(
            "Setting the extra features of the miio device failed.",
            self._device.set_extra_features,
            features,
        )

    async def async_reset_filter(self):
        """Reset the filter lifetime and usage."""
        if self._device_features & FEATURE_RESET_FILTER == 0:
            return

        await self._try_command(
            "Resetting the filter lifetime of the miio device failed.",
            self._device.reset_filter,
        )


class XiaomiAirPurifierMiot(XiaomiAirPurifier):
    """Representation of a Xiaomi Air Purifier (MiOT protocol)."""

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirpurifierMiotOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirpurifierMiotOperationMode[preset_mode.title()],
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirpurifierMiotLedBrightness(brightness),
        )


class XiaomiAirHumidifier(XiaomiGenericDevice):
    """Representation of a Xiaomi Air Humidifier."""

    def __init__(self, name, device, model, unique_id):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id)

        if self._model in [
            MODEL_AIRHUMIDIFIER_CA1,
            MODEL_AIRHUMIDIFIER_CB1,
            MODEL_AIRHUMIDIFIER_CB2,
        ]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Strong
            ]
        elif self._model == MODEL_AIRHUMIDIFIER_CA4:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._preset_modes = [mode.name for mode in AirhumidifierMiotOperationMode]
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER
            self._preset_modes = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Auto
            ]

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._state = state.is_on
            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )

        except DeviceException as ex:
            self._available = False
            _LOGGER.error("Got exception while fetching the state: %s", ex)

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirhumidifierOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierOperationMode[preset_mode.title()],
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device on failed.", self._device.set_led, True
        )

    async def async_set_led_off(self):
        """Turn the led off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_led,
            False,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirhumidifierLedBrightness(brightness),
        )

    async def async_set_target_humidity(self, humidity: int = 40):
        """Set the target humidity."""
        if self._device_features & FEATURE_SET_TARGET_HUMIDITY == 0:
            return

        await self._try_command(
            "Setting the target humidity of the miio device failed.",
            self._device.set_target_humidity,
            humidity,
        )

    async def async_set_dry_on(self):
        """Turn the dry mode on."""
        if self._device_features & FEATURE_SET_DRY == 0:
            return

        await self._try_command(
            "Turning the dry mode of the miio device on failed.",
            self._device.set_dry,
            True,
        )

    async def async_set_dry_off(self):
        """Turn the dry mode off."""
        if self._device_features & FEATURE_SET_DRY == 0:
            return

        await self._try_command(
            "Turning the dry mode of the miio device off failed.",
            self._device.set_dry,
            False,
        )

    async def async_set_clean_mode_on(self):
        """Turn the clean mode on."""
        if self._device_features & FEATURE_SET_CLEAN_MODE == 0:
            return

        await self._try_command(
            "Turning the clean mode of the miio device on failed.",
            self._device.set_clean_mode,
            True,
        )

    async def async_set_clean_mode_off(self):
        """Turn the clean mode off."""
        if self._device_features & FEATURE_SET_CLEAN_MODE == 0:
            return

        await self._try_command(
            "Turning the clean mode of the miio device off failed.",
            self._device.set_clean_mode,
            False,
        )


class XiaomiAirHumidifierMiot(XiaomiAirHumidifier):
    """Representation of a Xiaomi Air Humidifier (MiOT protocol)."""

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirhumidifierMiotOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    @property
    def button_pressed(self):
        """Return the last button pressed."""
        if self._state:
            return AirhumidifierPressedButton(
                self._state_attrs[ATTR_BUTTON_PRESSED]
            ).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierMiotOperationMode[preset_mode.title()],
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirhumidifierMiotLedBrightness(brightness),
        )

    async def async_set_motor_speed(self, motor_speed: int = 400):
        """Set the target motor speed."""
        if self._device_features & FEATURE_SET_MOTOR_SPEED == 0:
            return

        await self._try_command(
            "Setting the target motor speed of the miio device failed.",
            self._device.set_speed,
            motor_speed,
        )


class XiaomiAirHumidifierMjjsq(XiaomiAirHumidifier):
    """Representation of a Xiaomi Air Humidifier Mjjsq."""

    def __init__(self, name, device, model, unique_id):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id)

        if self._model == MODEL_AIRHUMIDIFIER_JSQ1:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ1
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ1
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ

        self._preset_modes = [mode.name for mode in AirhumidifierMjjsqOperationMode]
        self._state_attrs = {ATTR_MODEL: self._model}
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirhumidifierMjjsqOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierMjjsqOperationMode[preset_mode.title()],
        )

    async def async_set_wet_protection_on(self):
        """Turn the wet protection on."""
        if self._device_features & FEATURE_SET_WET_PROTECTION == 0:
            return

        await self._try_command(
            "Turning the wet protection of the miio device on failed.",
            self._device.set_wet_protection,
            True,
        )

    async def async_set_wet_protection_off(self):
        """Turn the wet protection off."""
        if self._device_features & FEATURE_SET_WET_PROTECTION == 0:
            return

        await self._try_command(
            "Turning the wet protection of the miio device off failed.",
            self._device.set_wet_protection,
            False,
        )


class XiaomiAirHumidifierJsqs(XiaomiAirHumidifier):
    """Representation of a Xiaomi Air Humidifier Jsqs."""

    def __init__(self, name, device, model, unique_id):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id)

        if self._model == MODEL_AIRHUMIDIFIER_JSQ5:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ5
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ5
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQS
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQS

        self._preset_modes = [mode.name for mode in AirhumidifierJsqsOperationMode]
        self._state_attrs = {ATTR_MODEL: self._model}
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirhumidifierJsqsOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierJsqsOperationMode[preset_mode.title()],
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device on failed.",
            self._device.set_light,
            True,
        )

    async def async_set_led_off(self):
        """Turn the led off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_light,
            False,
        )

    async def async_set_wet_protection_on(self):
        """Turn the wet protection on."""
        if self._device_features & FEATURE_SET_WET_PROTECTION == 0:
            return

        await self._try_command(
            "Turning the wet protection of the miio device on failed.",
            self._device.set_overwet_protect,
            True,
        )

    async def async_set_wet_protection_off(self):
        """Turn the wet protection off."""
        if self._device_features & FEATURE_SET_WET_PROTECTION == 0:
            return

        await self._try_command(
            "Turning the wet protection of the miio device off failed.",
            self._device.set_overwet_protect,
            False,
        )


class XiaomiAirHumidifierJsq(XiaomiAirHumidifier):
    """Representation of a Xiaomi Air Humidifier Jsq001."""

    def __init__(self, name, device, model, unique_id):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id)

        self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ
        self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ
        self._preset_modes = [mode.name for mode in AirhumidifierJsqOperationMode]
        self._state_attrs = {ATTR_MODEL: self._model}
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirhumidifierJsqOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""

        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierJsqOperationMode[preset_mode.title()],
        )

    async def async_set_led_brightness(self, brightness: int = 0):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirhumidifierJsqLedBrightness(brightness),
        )

    @property
    def led_brightness(self):
        """Return the current brightness."""
        if self._state:
            return AirhumidifierJsqLedBrightness(
                self._state_attrs[ATTR_LED_BRIGHTNESS]
            ).name

        return None


class XiaomiAirFresh(XiaomiGenericDevice):
    """Representation of a Xiaomi Air Fresh."""

    def __init__(self, name, device, model, unique_id):
        """Initialize the miio device."""
        super().__init__(name, device, model, unique_id)

        if self._model == MODEL_AIRFRESH_VA4:
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH_VA4
            self._device_features = FEATURE_FLAGS_AIRFRESH_VA4
        else:
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH
            self._device_features = FEATURE_FLAGS_AIRFRESH

        self._preset_modes = OPERATION_MODES_AIRFRESH
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._state = state.is_on
            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )

        except DeviceException as ex:
            self._available = False
            _LOGGER.error("Got exception while fetching the state: %s", ex)

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirfreshOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirfreshOperationMode[preset_mode.title()],
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device on failed.", self._device.set_led, True
        )

    async def async_set_led_off(self):
        """Turn the led off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_led,
            False,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            AirfreshLedBrightness(brightness),
        )

    async def async_set_extra_features(self, features: int = 1):
        """Set the extra features."""
        if self._device_features & FEATURE_SET_EXTRA_FEATURES == 0:
            return

        await self._try_command(
            "Setting the extra features of the miio device failed.",
            self._device.set_extra_features,
            features,
        )

    async def async_reset_filter(self):
        """Reset the filter lifetime and usage."""
        if self._device_features & FEATURE_RESET_FILTER == 0:
            return

        await self._try_command(
            "Resetting the filter lifetime of the miio device failed.",
            self._device.reset_filter,
        )

    async def async_set_ptc_on(self):
        """Turn the ptc on."""
        if self._device_features & FEATURE_SET_PTC == 0:
            return

        await self._try_command(
            "Turning the ptc of the miio device on failed.", self._device.set_ptc, True
        )

    async def async_set_ptc_off(self):
        """Turn the ptc off."""
        if self._device_features & FEATURE_SET_PTC == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_ptc,
            False,
        )


class XiaomiAirFreshT2017(XiaomiAirFresh):
    """Representation of a Xiaomi Air Fresh T2017."""

    def __init__(self, name, device, model, unique_id):
        """Initialize the miio device."""
        super().__init__(name, device, model, unique_id)

        if self._model == MODEL_AIRFRESH_T2017:
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH_T2017
            self._device_features = FEATURE_FLAGS_AIRFRESH_T2017
        else:
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH_A1
            self._device_features = FEATURE_FLAGS_AIRFRESH_A1

        self._preset_modes = OPERATION_MODES_AIRFRESH_T2017
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._state = state.is_on
            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )

        except DeviceException as ex:
            self._available = False
            _LOGGER.error("Got exception while fetching the state: %s", ex)

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return AirfreshT2017OperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            AirfreshT2017OperationMode[preset_mode.title()],
        )

    async def async_set_ptc_level(self, level: str):
        """Set the ptc level."""
        if self._device_features & FEATURE_SET_PTC_LEVEL == 0:
            return

        await self._try_command(
            "Setting the ptc level of the miio device failed.",
            self._device.set_ptc_level,
            AirfreshT2017PtcLevel[level.title()],
        )

    async def async_set_display_on(self):
        """Turn the display on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_display,
            True,
        )

    async def async_set_display_off(self):
        """Turn the display off."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.",
            self._device.set_display,
            False,
        )

    async def async_set_display_orientation(self, display_orientation: str):
        """Set the display orientation."""
        if self._device_features & FEATURE_SET_DISPLAY_ORIENTATION == 0:
            return

        await self._try_command(
            "Setting the display orientation of the miio device failed.",
            self._device.set_display_orientation,
            AirfreshT2017DisplayOrientation[display_orientation],
        )

    async def async_set_favorite_speed(self, speed: int = 1):
        """Set the favorite speed."""
        if self._device_features & FEATURE_SET_FAVORITE_SPEED == 0:
            return

        await self._try_command(
            "Setting the favorite speed of the miio device failed.",
            self._device.set_favorite_speed,
            speed,
        )

    async def async_reset_filter(self):
        """Reset the filter lifetime and usage."""
        if self._device_features & FEATURE_RESET_FILTER == 0:
            return

        await self._try_command(
            "Resetting the upper filter lifetime of the miio device failed.",
            self._device.reset_upper_filter,
        )
        await self._try_command(
            "Resetting the dust filter lifetime of the miio device failed.",
            self._device.reset_dust_filter,
        )


class XiaomiAirFreshA1(XiaomiAirFreshT2017):
    """Representation of a Xiaomi Air Fresh A1."""

    async def async_reset_filter(self):
        """Reset the filter lifetime and usage."""
        if self._device_features & FEATURE_RESET_FILTER == 0:
            return

        await self._try_command(
            "Resetting filter lifetime of the miio device failed.",
            self._device.reset_filter,
        )


class XiaomiFan(XiaomiGenericDevice):
    """Representation of a Xiaomi Pedestal Fan."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_FLAGS_FAN
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN
        self._percentage = None
        self._preset_modes = list(FAN_PRESET_MODES)
        self._preset_mode = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def supported_features(self) -> int:
        """Supported features."""
        return (
            SUPPORT_SET_SPEED
            | SUPPORT_PRESET_MODE
            | SUPPORT_OSCILLATE
            | SUPPORT_DIRECTION
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._oscillate = state.oscillate
            self._natural_mode = state.natural_speed != 0
            self._state = state.is_on

            if self._natural_mode:
                for preset_mode, range in FAN_PRESET_MODES.items():
                    if state.natural_speed in range:
                        self._preset_mode = preset_mode
                        self._percentage = state.natural_speed
                        break
            else:
                for preset_mode, range in FAN_PRESET_MODES.items():
                    if state.direct_speed in range:
                        self._preset_mode = preset_mode
                        self._percentage = state.direct_speed
                        break

            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )
            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    @property
    def percentage(self):
        """Return the current speed."""
        return self._percentage

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        return self._preset_mode

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if preset_mode == SPEED_OFF:
            await self.async_turn_off()
            return

        if self._natural_mode:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_natural_speed,
                FAN_PRESET_MODE_VALUES[preset_mode],
            )
        else:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_direct_speed,
                FAN_PRESET_MODE_VALUES[preset_mode],
            )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        _LOGGER.debug("Setting the fan speed percentage to: %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        if self._natural_mode:
            await self._try_command(
                "Setting fan speed percentage of the miio device failed.",
                self._device.set_natural_speed,
                percentage,
            )
        else:
            await self._try_command(
                "Setting fan speed percentage of the miio device failed.",
                self._device.set_direct_speed,
                percentage,
            )

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction == "forward":
            direction = "right"

        if direction == "reverse":
            direction = "left"

        if self._oscillate:
            await self._try_command(
                "Setting oscillate off of the miio device failed.",
                self._device.set_oscillate,
                False,
            )

        await self._try_command(
            "Setting move direction of the miio device failed.",
            self._device.set_rotate,
            FanMoveDirection(direction),
        )

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._oscillate

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        if oscillating:
            await self._try_command(
                "Setting oscillate on of the miio device failed.",
                self._device.set_oscillate,
                True,
            )
        else:
            await self._try_command(
                "Setting oscillate off of the miio device failed.",
                self._device.set_oscillate,
                False,
            )

    async def async_set_oscillation_angle(self, angle: int) -> None:
        """Set oscillation angle."""
        if self._device_features & FEATURE_SET_OSCILLATION_ANGLE == 0:
            return

        await self._try_command(
            "Setting angle of the miio device failed.", self._device.set_angle, angle
        )

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown * 60,
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            FanLedBrightness(brightness),
        )

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        self._natural_mode = True
        await self.async_set_percentage(self._percentage)

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        self._natural_mode = False
        await self.async_set_percentage(self._percentage)


class XiaomiFanP5(XiaomiFan):
    """Representation of a Xiaomi Pedestal Fan P5."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_FLAGS_FAN_P5
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_P5
        self._percentage = None
        self._preset_modes = list(FAN_PRESET_MODES)
        self._preset_mode = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._percentage = state.speed
            self._oscillate = state.oscillate
            self._natural_mode = state.mode == FanOperationMode.Nature
            self._state = state.is_on

            for preset_mode, range in FAN_PRESET_MODES.items():
                if state.speed in range:
                    self._preset_mode = preset_mode
                    break

            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )

            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if preset_mode == SPEED_OFF:
            await self.async_turn_off()
            return

        await self._try_command(
            "Setting fan speed of the miio device failed.",
            self._device.set_speed,
            FAN_PRESET_MODE_VALUES_P5[preset_mode],
        )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        _LOGGER.debug("Setting the fan speed percentage to: %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        await self._try_command(
            "Setting fan speed percentage of the miio device failed.",
            self._device.set_speed,
            percentage,
        )

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Turning on natural mode of the miio device failed.",
            self._device.set_mode,
            FanOperationMode.Nature,
        )

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Turning on natural mode of the miio device failed.",
            self._device.set_mode,
            FanOperationMode.Normal,
        )

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown,
        )


class XiaomiFanMiot(XiaomiFanP5):
    """Representation of a Xiaomi Pedestal Fan P9, P10, P11."""


class XiaomiFanLeshow(XiaomiGenericDevice):
    """Representation of a Xiaomi Fan Leshow SS4."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_FLAGS_FAN_LESHOW_SS4
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_LESHOW_SS4
        self._percentage = None
        self._preset_modes = [mode.name for mode in FanLeshowOperationMode]
        self._oscillate = None

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def supported_features(self) -> int:
        """Supported features."""
        return SUPPORT_SET_SPEED | SUPPORT_PRESET_MODE | SUPPORT_OSCILLATE

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._percentage = state.speed
            self._oscillate = state.oscillate
            self._state = state.is_on

            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )
            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    @property
    def percentage(self):
        """Return the current speed."""
        return self._percentage

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return FanLeshowOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode,
            FanLeshowOperationMode[preset_mode.title()],
        )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        _LOGGER.debug("Setting the fan speed percentage to: %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        await self._try_command(
            "Setting fan speed percentage of the miio device failed.",
            self._device.set_speed,
            percentage,
        )

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._oscillate

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        if oscillating:
            await self._try_command(
                "Setting oscillate on of the miio device failed.",
                self._device.set_oscillate,
                True,
            )
        else:
            await self._try_command(
                "Setting oscillate off of the miio device failed.",
                self._device.set_oscillate,
                False,
            )

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown,
        )


class XiaomiFan1C(XiaomiFan):
    """Representation of a Xiaomi Fan 1C."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_FLAGS_FAN_1C
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_1C
        self._preset_modes = list(FAN_PRESET_MODES_1C)
        self._oscillate = None

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def supported_features(self) -> int:
        """Supported features."""
        return SUPPORT_SET_SPEED | SUPPORT_PRESET_MODE | SUPPORT_OSCILLATE

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._oscillate = state.oscillate
            self._state = state.is_on

            for preset_mode, value in FAN_PRESET_MODES_1C.items():
                if state.speed == value:
                    self._preset_mode = preset_mode

            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )
            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        return ordered_list_item_to_percentage(FAN_SPEEDS_1C, self._preset_mode)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return len(FAN_SPEEDS_1C)

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return self._preset_modes

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            return self._preset_mode

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)

        if not self._state:
            await self._try_command(
                "Turning the miio device on failed.", self._device.on
            )
        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_speed,
            FAN_PRESET_MODES_1C[preset_mode],
        )

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        _LOGGER.debug("Setting the fan speed percentage to: %s", percentage)

        if percentage == 0:
            await self.async_turn_off()
            return

        if not self._state:
            await self._try_command(
                "Turning the miio device on failed.", self._device.on
            )
        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_speed,
            FAN_PRESET_MODES_1C[
                percentage_to_ordered_list_item(FAN_SPEEDS_1C, percentage)
            ],
        )

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._oscillate

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        if oscillating:
            await self._try_command(
                "Setting oscillate on of the miio device failed.",
                self._device.set_oscillate,
                True,
            )
        else:
            await self._try_command(
                "Setting oscillate off of the miio device failed.",
                self._device.set_oscillate,
                False,
            )

    async def async_set_delay_off(self, delay_off_countdown: int) -> None:
        """Set scheduled off timer in minutes."""

        await self._try_command(
            "Setting delay off miio device failed.",
            self._device.delay_off,
            delay_off_countdown,
        )

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Setting fan natural mode of the miio device failed.",
            self._device.set_mode,
            FanOperationMode.Nature,
        )

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        await self._try_command(
            "Setting fan natural mode of the miio device failed.",
            self._device.set_mode,
            FanOperationMode.Normal,
        )


class XiaomiAirDog(XiaomiGenericDevice):
    """Representation of a Xiaomi AirDog air purifiers."""

    def __init__(self, name, device, model, unique_id, retries=0):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_FLAGS_AIRPURIFIER_AIRDOG

        if self._model == MODEL_AIRPURIFIER_AIRDOG_X7SM:
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X7SM
        else:
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_AIRDOG_X3

        self._preset_modes_to_mode_speed = {
            "Auto": (AirDogOperationMode("auto"), 1),
            "Night mode": (AirDogOperationMode("sleep"), 1),
            "Speed 1": (AirDogOperationMode("manual"), 1),
            "Speed 2": (AirDogOperationMode("manual"), 2),
            "Speed 3": (AirDogOperationMode("manual"), 3),
            "Speed 4": (AirDogOperationMode("manual"), 4),
        }
        if self._model == MODEL_AIRPURIFIER_AIRDOG_X7SM:
            self._preset_modes_to_mode_speed["Speed 5"] = (
                AirDogOperationMode("Manual"),
                5,
            )

        self._mode_speed_to_preset_modes = {}
        for key, value in self._preset_modes_to_mode_speed.items():
            self._mode_speed_to_preset_modes[value] = key

        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    async def async_update(self):
        """Fetch state from the device."""
        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_executor_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._state = state.is_on
            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )

            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    @property
    def preset_modes(self):
        """Get the list of available preset modes."""
        return list(self._preset_modes_to_mode_speed.keys())

    @property
    def preset_mode(self):
        """Get the current preset mode."""
        if self._state:
            # There are invalid modes, such as 'Auto 2'. There are no presets for them
            if (
                AirDogOperationMode(self._state_attrs[ATTR_MODE]),
                self._state_attrs[ATTR_SPEED],
            ) in self._mode_speed_to_preset_modes:
                return self._mode_speed_to_preset_modes[
                    (
                        AirDogOperationMode(self._state_attrs[ATTR_MODE]),
                        self._state_attrs[ATTR_SPEED],
                    )
                ]

        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        _LOGGER.debug("Setting the preset mode to: %s", preset_mode)
        _LOGGER.debug(
            "Calling set_mode_and_speed with parameters: %s",
            self._preset_modes_to_mode_speed[preset_mode],
        )

        # Following is true on AirDogX5 with firmware 1.3.5_0005. Maybe this is different for other models. Needs testing

        # It looks like the device was not designed to switch from any arbitrary mode to any other mode.
        # Some of the combinations produce unexpected results
        #
        # For example, switching from 'Auto' to 'Speed X' switches to Manual mode, but always sets speed to 1, regardless of the speed parameter.
        #
        # Switching from 'Night mode' to 'Speed X' sets device in Auto mode with speed X.
        # Tihs 'Auto X' state is quite strange and does not seem to be useful.
        # Furthermore, we request Manual mode and get Auto.
        # Switching from 'Auto X' mode to 'Manual X' works just fine.
        # Switching from 'Auto X' mode to 'Manual Y' switches to 'Manual X'.

        # Here is a full table of device behaviour

        # FROM          TO              RESULT
        #'Night mode' ->
        #               'Auto'          Good
        #               'Speed 1'       'Auto 1' + repeat -> Good
        #               'Speed 2'       'Auto 2' + repeat -> Good
        #               'Speed 3'       'Auto 3' + repeat -> Good
        #               'Speed 4'       'Auto 4' + repeat -> Good
        #'Speed 1'
        #               'Night mode'    Good
        #               'Auto'    Good
        #'Speed 2' ->
        #               'Night mode'    Good
        #               'Auto'    Good
        #'Speed 3' ->
        #               'Night mode'    Good
        #               'Auto'    Good
        #'Speed 4' ->
        #               'Night mode'    Good
        #'Auto'->
        #               'Night mode'    Good
        #               'Speed 1'       Good
        #               'Speed 2'       'Speed 1' + repeat ->  Good
        #               'Speed 3'       'Speed 1' + repeat ->  Good
        #               'Speed 4'       'Speed 1' + repeat ->  Good

        # To allow switching from any mode to any other mode command is repeated twice when switching is from 'Night mode' or 'Auto' to 'Speed X'.

        await self._try_command(
            "Setting preset mode of the miio device failed.",
            self._device.set_mode_and_speed,
            *self._preset_modes_to_mode_speed[
                preset_mode
            ],  # Corresponding mode and speed parameters are in tuple
        )

        if (
            self._state_attrs[ATTR_MODE] in ("auto", "sleep")
            and self._preset_modes_to_mode_speed[preset_mode][0].value == "manual"
        ):
            await self._try_command(
                "Setting preset mode of the miio device failed.",
                self._device.set_mode_and_speed,
                *self._preset_modes_to_mode_speed[
                    preset_mode
                ],  # Corresponding mode and speed parameters are in tuple
            )

        self._state_attrs.update(
            {
                ATTR_MODE: self._preset_modes_to_mode_speed[preset_mode][0].value,
                ATTR_SPEED: self._preset_modes_to_mode_speed[preset_mode][1],
            }
        )
        self._skip_update = True

    async def async_set_filters_cleaned(self):
        """Set filters cleaned."""
        await self._try_command(
            "Setting filters cleaned failed.",
            self._device.set_filters_cleaned,
        )

    async def async_turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:
        """Turn the device on."""
        await super().async_turn_on(speed, percentage, preset_mode, **kwargs)

        self._state = True
        self._skip_update = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the device off."""
        await super().async_turn_off(**kwargs)

        self._state = False
        self._skip_update = True

    async def async_set_child_lock_on(self):
        """Turn the child lock on."""
        await super().async_set_child_lock_on()
        self._state_attrs.update(
            {
                ATTR_CHILD_LOCK: True,
            }
        )
        self._skip_update = True

    async def async_set_child_lock_off(self):
        """Turn the child lock off."""
        await super().async_set_child_lock_off()
        self._state_attrs.update(
            {
                ATTR_CHILD_LOCK: False,
            }
        )
        self._skip_update = True

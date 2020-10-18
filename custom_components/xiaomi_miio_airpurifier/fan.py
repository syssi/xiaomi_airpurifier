"""Support for Xiaomi Mi Air Purifier and Xiaomi Mi Air Humidifier."""
import asyncio
from enum import Enum
from functools import partial
import logging

from miio import (  # pylint: disable=import-error
    AirFresh,
    AirHumidifier,
    AirHumidifierJsq,
    AirHumidifierMiot,
    AirHumidifierMjjsq,
    AirPurifier,
    AirPurifierMiot,
    Device,
    DeviceException,
    Fan,
    FanMiot,
    FanP5,
)
from miio.airfresh import (  # pylint: disable=import-error, import-error
    LedBrightness as AirfreshLedBrightness,
    OperationMode as AirfreshOperationMode,
)
from miio.airhumidifier import (  # pylint: disable=import-error, import-error
    LedBrightness as AirhumidifierLedBrightness,
    OperationMode as AirhumidifierOperationMode,
)
from miio.airhumidifier_jsq import (  # pylint: disable=import-error, import-error
    LedBrightness as AirhumidifierJsqLedBrightness,
    OperationMode as AirhumidifierJsqOperationMode,
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
from miio.airpurifier_miot import (  # pylint: disable=import-error, import-error
    LedBrightness as AirpurifierMiotLedBrightness,
    OperationMode as AirpurifierMiotOperationMode,
)
from miio.fan import (  # pylint: disable=import-error, import-error
    LedBrightness as FanLedBrightness,
    MoveDirection as FanMoveDirection,
    OperationMode as FanOperationMode,
)
import voluptuous as vol

from homeassistant.components.fan import (
    ATTR_SPEED,
    PLATFORM_SCHEMA,
    SPEED_HIGH,
    SPEED_LOW,
    SPEED_MEDIUM,
    SPEED_OFF,
    SUPPORT_DIRECTION,
    SUPPORT_OSCILLATE,
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

MODEL_AIRHUMIDIFIER_V1 = "zhimi.humidifier.v1"
MODEL_AIRHUMIDIFIER_CA1 = "zhimi.humidifier.ca1"
MODEL_AIRHUMIDIFIER_CA4 = "zhimi.humidifier.ca4"
MODEL_AIRHUMIDIFIER_CB1 = "zhimi.humidifier.cb1"
MODEL_AIRHUMIDIFIER_MJJSQ = "deerma.humidifier.mjjsq"
MODEL_AIRHUMIDIFIER_JSQ1 = "deerma.humidifier.jsq1"
MODEL_AIRHUMIDIFIER_JSQ001 = "shuii.humidifier.jsq001"

MODEL_AIRFRESH_VA2 = "zhimi.airfresh.va2"

MODEL_FAN_V2 = "zhimi.fan.v2"
MODEL_FAN_V3 = "zhimi.fan.v3"
MODEL_FAN_SA1 = "zhimi.fan.sa1"
MODEL_FAN_ZA1 = "zhimi.fan.za1"
MODEL_FAN_ZA3 = "zhimi.fan.za3"
MODEL_FAN_ZA4 = "zhimi.fan.za4"
MODEL_FAN_P5 = "dmaker.fan.p5"
MODEL_FAN_P9 = "dmaker.fan.p9"
MODEL_FAN_P10 = "dmaker.fan.p10"
MODEL_FAN_P11 = "dmaker.fan.p11"

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
                MODEL_AIRHUMIDIFIER_V1,
                MODEL_AIRHUMIDIFIER_CA1,
                MODEL_AIRHUMIDIFIER_CA4,
                MODEL_AIRHUMIDIFIER_CB1,
                MODEL_AIRHUMIDIFIER_MJJSQ,
                MODEL_AIRHUMIDIFIER_JSQ1,
                MODEL_AIRHUMIDIFIER_JSQ001,
                MODEL_AIRFRESH_VA2,
                MODEL_FAN_V2,
                MODEL_FAN_V3,
                MODEL_FAN_SA1,
                MODEL_FAN_ZA1,
                MODEL_FAN_ZA3,
                MODEL_FAN_ZA4,
                MODEL_FAN_P5,
                MODEL_FAN_P9,
                MODEL_FAN_P10,
                MODEL_FAN_P11,
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

# Air Humidifier MJJSQ and JSQ1
ATTR_NO_WATER = "no_water"
ATTR_WATER_TANK_DETACHED = "water_tank_detached"

# Air Humidifier JSQ001
ATTR_LID_OPENED = "lid_opened"

# Air Fresh
ATTR_CO2 = "co2"

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

PURIFIER_MIOT = [MODEL_AIRPURIFIER_3, MODEL_AIRPURIFIER_3H]
HUMIDIFIER_MIOT = [MODEL_AIRHUMIDIFIER_CA4]

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
    ATTR_DEPTH: "depth",
    ATTR_DRY: "dry",
    ATTR_CHILD_LOCK: "child_lock",
    ATTR_LED_BRIGHTNESS: "led_brightness",
    ATTR_USE_TIME: "use_time",
    ATTR_HARDWARE_VERSION: "hardware_version",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4 = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_ACTUAL_MOTOR_SPEED: "actual_speed",
    ATTR_BUTTON_PRESSED: "button_pressed",
    ATTR_DRY: "dry",
    ATTR_FAHRENHEIT: "fahrenheit",
    ATTR_MOTOR_SPEED: "motor_speed",
    ATTR_WATER_LEVEL: "water_level",
}

AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ_AND_JSQ1 = {
    **AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_COMMON,
    ATTR_LED: "led",
    ATTR_NO_WATER: "no_water",
    ATTR_WATER_TANK_DETACHED: "water_tank_detached",
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

FAN_SPEED_LEVEL1 = "Level 1"
FAN_SPEED_LEVEL2 = "Level 2"
FAN_SPEED_LEVEL3 = "Level 3"
FAN_SPEED_LEVEL4 = "Level 4"

FAN_SPEED_LIST = {
    SPEED_OFF: range(0, 1),
    FAN_SPEED_LEVEL1: range(1, 26),
    FAN_SPEED_LEVEL2: range(26, 51),
    FAN_SPEED_LEVEL3: range(51, 76),
    FAN_SPEED_LEVEL4: range(76, 101),
}

FAN_SPEED_VALUES = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 74,
    FAN_SPEED_LEVEL4: 100,
}

FAN_SPEED_VALUES_P5 = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
    FAN_SPEED_LEVEL3: 70,
    FAN_SPEED_LEVEL4: 100,
}

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

# Smart Fan
FEATURE_SET_OSCILLATION_ANGLE = 4096
FEATURE_SET_NATURAL_MODE = 8192

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
)

FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ_AND_JSQ1 = (
    FEATURE_SET_BUZZER | FEATURE_SET_LED | FEATURE_SET_TARGET_HUMIDITY
)

FEATURE_FLAGS_AIRHUMIDIFIER_JSQ = (
    FEATURE_SET_BUZZER
    | FEATURE_SET_LED
    | SUPPORT_SET_SPEED
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

# Smart Fan
SERVICE_SET_DELAY_OFF = "fan_set_delay_off"
SERVICE_SET_OSCILLATION_ANGLE = "fan_set_oscillation_angle"
SERVICE_SET_NATURAL_MODE_ON = "fan_set_natural_mode_on"
SERVICE_SET_NATURAL_MODE_OFF = "fan_set_natural_mode_off"

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

SERVICE_SCHEMA_MOTOR_SPEED = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_MOTOR_SPEED): vol.All(
            vol.Coerce(int), vol.Clamp(min=200, max=2000)
        )
    }
)

SERVICE_SCHEMA_OSCILLATION_ANGLE = AIRPURIFIER_SERVICE_SCHEMA.extend(
    {vol.Required(ATTR_ANGLE): vol.All(vol.Coerce(int), vol.In([30, 60, 90, 120]))}
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
        device = XiaomiAirPurifierMiot(name, air_purifier, model, unique_id)
    elif model.startswith("zhimi.airpurifier."):
        air_purifier = AirPurifier(host, token)
        device = XiaomiAirPurifier(name, air_purifier, model, unique_id)
    elif model in HUMIDIFIER_MIOT:
        air_humidifier = AirHumidifierMiot(host, token)
        device = XiaomiAirHumidifierMiot(name, air_humidifier, model, unique_id)
    elif model.startswith("zhimi.humidifier."):
        air_humidifier = AirHumidifier(host, token, model=model)
        device = XiaomiAirHumidifier(name, air_humidifier, model, unique_id)
    elif model in [MODEL_AIRHUMIDIFIER_MJJSQ, MODEL_AIRHUMIDIFIER_JSQ1]:
        air_humidifier = AirHumidifierMjjsq(host, token, model=model)
        device = XiaomiAirHumidifierMjjsq(name, air_humidifier, model, unique_id)
    elif model == MODEL_AIRHUMIDIFIER_JSQ001:
        air_humidifier = AirHumidifierJsq(host, token, model=model)
        device = XiaomiAirHumidifierJsq(name, air_humidifier, model, unique_id)
    elif model.startswith("zhimi.airfresh."):
        air_fresh = AirFresh(host, token)
        device = XiaomiAirFresh(name, air_fresh, model, unique_id)
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
    elif model in [MODEL_FAN_P9, MODEL_FAN_P10, MODEL_FAN_P11]:
        fan = FanMiot(host, token, model=model)
        device = XiaomiFanP5(name, fan, model, unique_id, retries)
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

    def __init__(self, name, device, model, unique_id, retries):
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
        return SUPPORT_SET_SPEED

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
    def device_state_attributes(self):
        """Return the state attributes of the device."""
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

    async def async_turn_on(self, speed: str = None, **kwargs) -> None:
        """Turn the device on."""
        if speed:
            # If operation mode was set the device must not be turned on.
            result = await self.async_set_speed(speed)
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

    def __init__(self, name, device, model, unique_id):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id)

        if self._model == MODEL_AIRPURIFIER_PRO:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_PRO
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO
            self._speed_list = OPERATION_MODES_AIRPURIFIER_PRO
        elif self._model == MODEL_AIRPURIFIER_PRO_V7:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_PRO_V7
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_PRO_V7
            self._speed_list = OPERATION_MODES_AIRPURIFIER_PRO_V7
        elif self._model == MODEL_AIRPURIFIER_2S:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_2S
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_2S
            self._speed_list = OPERATION_MODES_AIRPURIFIER_2S
        elif self._model == MODEL_AIRPURIFIER_2H:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_2H
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_2H
            self._speed_list = OPERATION_MODES_AIRPURIFIER_2H
        elif self._model == MODEL_AIRPURIFIER_3 or self._model == MODEL_AIRPURIFIER_3H:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_3
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_3
            self._speed_list = OPERATION_MODES_AIRPURIFIER_3
        elif self._model == MODEL_AIRPURIFIER_V3:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER_V3
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER_V3
            self._speed_list = OPERATION_MODES_AIRPURIFIER_V3
        else:
            self._device_features = FEATURE_FLAGS_AIRPURIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRPURIFIER
            self._speed_list = OPERATION_MODES_AIRPURIFIER

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
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return self._speed_list

    @property
    def speed(self):
        """Return the current speed."""
        if self._state:
            return AirpurifierOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the operation mode to: %s", speed)

        await self._try_command(
            "Setting operation mode of the miio device failed.",
            self._device.set_mode,
            AirpurifierOperationMode[speed.title()],
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.", self._device.set_led, True
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
    def speed(self):
        """Return the current speed."""
        if self._state:
            return AirpurifierMiotOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the operation mode to: %s", speed)

        await self._try_command(
            "Setting operation mode of the miio device failed.",
            self._device.set_mode,
            AirpurifierMiotOperationMode[speed.title()],
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

        if self._model in [MODEL_AIRHUMIDIFIER_CA1, MODEL_AIRHUMIDIFIER_CB1]:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA_AND_CB
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA_AND_CB
            self._speed_list = [
                mode.name
                for mode in AirhumidifierOperationMode
                if mode is not AirhumidifierOperationMode.Strong
            ]
        elif self._model == MODEL_AIRHUMIDIFIER_CA4:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_CA4
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_CA4
            self._speed_list = [SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH]
        else:
            self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER
            self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER
            self._speed_list = [
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
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return self._speed_list

    @property
    def speed(self):
        """Return the current speed."""
        if self._state:
            return AirhumidifierOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the operation mode to: %s", speed)

        await self._try_command(
            "Setting operation mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierOperationMode[speed.title()],
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.", self._device.set_led, True
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
            "Turning the dry mode of the miio device off failed.",
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


class XiaomiAirHumidifierMiot(XiaomiAirHumidifier):
    """Representation of a Xiaomi Air Humidifier (MiOT protocol)."""

    @property
    def speed(self):
        """Return the current speed."""
        if self._state:
            if (
                AirhumidifierMiotOperationMode(self._state_attrs[ATTR_MODE])
                == AirhumidifierMiotOperationMode.Low
            ):
                return SPEED_LOW
            if (
                AirhumidifierMiotOperationMode(self._state_attrs[ATTR_MODE])
                == AirhumidifierMiotOperationMode.Mid
            ):
                return SPEED_MEDIUM
            if (
                AirhumidifierMiotOperationMode(self._state_attrs[ATTR_MODE])
                == AirhumidifierMiotOperationMode.High
            ):
                return SPEED_HIGH

        return None

    @property
    def button_pressed(self):
        """Return the last button pressed."""
        if self._state:
            return AirhumidifierPressedButton(
                self._state_attrs[ATTR_BUTTON_PRESSED]
            ).name

        return None

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""

        translated_speed = 0

        if speed == SPEED_LOW:
            translated_speed = AirhumidifierMiotOperationMode.Low
        elif speed == SPEED_MEDIUM:
            translated_speed = AirhumidifierMiotOperationMode.Mid
        elif speed == SPEED_HIGH:
            translated_speed = AirhumidifierMiotOperationMode.High
        else:
            return None

        await self._try_command(
            "Setting operation mode of the miio device failed.",
            self._device.set_mode,
            translated_speed,
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

        self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_MJJSQ_AND_JSQ1
        self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_MJJSQ_AND_JSQ1
        self._speed_list = [mode.name for mode in AirhumidifierMjjsqOperationMode]
        self._state_attrs = {ATTR_MODEL: self._model}
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def speed(self):
        """Return the current speed."""
        if self._state:
            return AirhumidifierMjjsqOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the operation mode to: %s", speed)

        await self._try_command(
            "Setting operation mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierMjjsqOperationMode[speed.title()],
        )


class XiaomiAirHumidifierJsq(XiaomiAirHumidifier):
    """Representation of a Xiaomi Air Humidifier Jsq001."""

    def __init__(self, name, device, model, unique_id):
        """Initialize the plug switch."""
        super().__init__(name, device, model, unique_id)

        self._device_features = FEATURE_FLAGS_AIRHUMIDIFIER_JSQ
        self._available_attributes = AVAILABLE_ATTRIBUTES_AIRHUMIDIFIER_JSQ
        self._speed_list = [mode.name for mode in AirhumidifierJsqOperationMode]
        self._state_attrs = {ATTR_MODEL: self._model}
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def speed(self):
        """Return the current speed."""
        if self._state:
            return AirhumidifierJsqOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the operation mode to: %s", speed)

        await self._try_command(
            "Setting operation mode of the miio device failed.",
            self._device.set_mode,
            AirhumidifierJsqOperationMode[speed.title()],
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

        self._device_features = FEATURE_FLAGS_AIRFRESH
        self._available_attributes = AVAILABLE_ATTRIBUTES_AIRFRESH
        self._speed_list = OPERATION_MODES_AIRFRESH
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
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return self._speed_list

    @property
    def speed(self):
        """Return the current speed."""
        if self._state:
            return AirfreshOperationMode(self._state_attrs[ATTR_MODE]).name

        return None

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the operation mode to: %s", speed)

        await self._try_command(
            "Setting operation mode of the miio device failed.",
            self._device.set_mode,
            AirfreshOperationMode[speed.title()],
        )

    async def async_set_led_on(self):
        """Turn the led on."""
        if self._device_features & FEATURE_SET_LED == 0:
            return

        await self._try_command(
            "Turning the led of the miio device off failed.", self._device.set_led, True
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


class XiaomiFan(XiaomiGenericDevice):
    """Representation of a Xiaomi Pedestal Fan."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_FLAGS_FAN
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN
        self._speed_list = list(FAN_SPEED_LIST)
        self._speed = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs[ATTR_SPEED] = None
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def supported_features(self) -> int:
        """Supported features."""
        return SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION

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
                for level, range in FAN_SPEED_LIST.items():
                    if state.natural_speed in range:
                        self._speed = level
                        self._state_attrs[ATTR_SPEED] = level
                        break
            else:
                for level, range in FAN_SPEED_LIST.items():
                    if state.direct_speed in range:
                        self._speed = level
                        self._state_attrs[ATTR_SPEED] = level
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
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return self._speed_list

    @property
    def speed(self):
        """Return the current speed."""
        return self._speed

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the fan speed to: %s", speed)

        if speed.isdigit():
            speed = int(speed)

        if speed in [SPEED_OFF, 0]:
            await self.async_turn_off()
            return

        # Map speed level to speed
        if speed in FAN_SPEED_VALUES:
            speed = FAN_SPEED_VALUES[speed]

        if self._natural_mode:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_natural_speed,
                speed,
            )
        else:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_direct_speed,
                speed,
            )

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        if direction in ["left", "right"]:
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
        await self.async_set_speed(self._speed)

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        self._natural_mode = False
        await self.async_set_speed(self._speed)


class XiaomiFanP5(XiaomiFan):
    """Representation of a Xiaomi Pedestal Fan P5."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_FLAGS_FAN_P5
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN_P5
        self._speed_list = list(FAN_SPEED_LIST)
        self._speed = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs[ATTR_SPEED] = None
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
            self._oscillate = state.oscillate
            self._natural_mode = state.mode == FanOperationMode.Nature
            self._state = state.is_on

            for level, range in FAN_SPEED_LIST.items():
                if state.speed in range:
                    self._speed = level
                    self._state_attrs[ATTR_SPEED] = level
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

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the fan speed to: %s", speed)

        if speed.isdigit():
            speed = int(speed)

        if speed in [SPEED_OFF, 0]:
            await self.async_turn_off()
            return

        # Map speed level to speed
        if speed in FAN_SPEED_VALUES_P5:
            speed = FAN_SPEED_VALUES_P5[speed]

        await self._try_command(
            "Setting fan speed of the miio device failed.",
            self._device.set_speed,
            speed,
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

# Xiaomi Mi Air Purifier & Xiaomi Mi Air Humidifier

This is a custom component for home assistant to integrate the Xiaomi Mi Air Purifier 2, Air Purifier 2S, Air Purifier Pro, Air Humidifier, Air Fresh and Pedestal Fan.

Please follow the instructions on [Retrieving the Access Token](https://home-assistant.io/components/xiaomi/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

Credits: Thanks to [Rytilahti](https://github.com/rytilahti/python-miio) for all the work.

## Supported devices

| Name                   | Model                  | Model no. |
| ---------------------- | ---------------------- | --------- |
| Air Purifier           | zhimi.airpurifier.v1   | |
| Air Purifier 2         | zhimi.airpurifier.v2   | FJY4006CN |
| Air Purifier V3        | zhimi.airpurifier.v3   | |
| Air Purifier V5        | zhimi.airpurifier.v5   | |
| Air Purifier Pro       | zhimi.airpurifier.v6   | |
| Air Purifier Pro V7    | zhimi.airpurifier.v7   | |
| Air Purifier 2 (mini)  | zhimi.airpurifier.m1   | |
| Air Purifier (mini)    | zhimi.airpurifier.m2   | |
| Air Purifier MA1       | zhimi.airpurifier.ma1  | |
| Air Purifier MA2       | zhimi.airpurifier.ma2  | |
| Air Purifier 2S        | zhimi.airpurifier.mc1  | |
| Air Purifier Super     | zhimi.airpurifier.sa1  | |
| Air Purifier Super 2   | zhimi.airpurifier.sa2  | |
| Air Purifier 3 (2019)  | zhimi.airpurifier.ma4  | |
| Air Purifier 3H (2019) | zhimi.airpurifier.mb3  | |
| Air Humidifier         | zhimi.humidifier.v1    | |
| Air Humidifier CA1     | zhimi.humidifier.ca1   | |
| Air Humidifier CA4     | zhimi.humidifier.ca4   | |
| Air Humidifier CB1     | zhimi.humidifier.cb1   | |
| Air Humidifier MJJSQ   | deerma.humidifier.mjjsq   | |
| Air Humidifier JSQ1    | deerma.humidifier.jsq1    | |
| Air Fresh VA2          | zhimi.airfresh.va2     | |
| Pedestal Fan Fan V2    | zhimi.fan.v2           | |
| Pedestal Fan Fan V3    | zhimi.fan.v3           | |
| Pedestal Fan Fan SA1   | zhimi.fan.sa1          | |
| Pedestal Fan Fan ZA1   | zhimi.fan.za1          | |
| Pedestal Fan Fan ZA3   | zhimi.fan.za3          | |
| Pedestal Fan Fan ZA4   | zhimi.fan.za4          | |
| Pedestal Fan Fan P5    | dmaker.fan.p5          | |
  Pedestal Fan Fan P10   | dmaker.fan.p10         | |
  Pedestal Fan Fan P11   | dmaker.fan.p11         | |
  Pedestal Fan Fan P12   | dmaker.fan.p12         | |
 

## Features

### Air Purifier 2 et al.

- Power (on, off)
- Operation modes (auto, silent, favorite, idle)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off), LED brightness (bright, dim, off)
- Favorite Level (0...16)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `aqi`
  - `mode`
  - `filter_hours_used`
  - `filter_life_remaining`
  - `favorite_level`
  - `child_lock`
  - `led`
  - `motor_speed`
  - `average_aqi`
  - `purify_volume`
  - `learn_mode`
  - `sleep_time`
  - `sleep_mode_learn_count`
  - `extra_features`
  - `turbo_mode_supported`
  - `auto_detect`
  - `use_time`
  - `button_pressed`
  - `buzzer`
  - `led_brightness`
  - `sleep_mode`

### Air Purifier 2H (zhimi.airpurifier.mc2)

- Power (on, off)
- Operation modes (auto, silent, favorite, idle)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off), LED brightness (bright, dim, off)
- Favorite Level (0...16)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `aqi`
  - `mode`
  - `filter_hours_used`
  - `filter_life_remaining`
  - `favorite_level`
  - `child_lock`
  - `led`
  - `motor_speed`
  - `average_aqi`
  - `learn_mode`
  - `extra_features`
  - `turbo_mode_supported`
  - `buzzer`
  - `led_brightness`

### Air Purifier Pro (zhimi.airpurifier.v6)

- Power (on, off)
- Operation modes (auto, silent, favorite)
- Child lock (on, off)
- LED (on, off)
- Favorite Level (0...16)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `aqi`
  - `mode`
  - `filter_hours_used`
  - `filter_life_remaining`
  - `favorite_level`
  - `child_lock`
  - `led`
  - `motor_speed`
  - `average_aqi`
  - `purify_volume`
  - `learn_mode`
  - `sleep_time`
  - `sleep_mode_learn_count`
  - `extra_features`
  - `turbo_mode_supported`
  - `auto_detect`
  - `use_time`
  - `button_pressed`
  - `filter_rfid_product_id`
  - `filter_rfid_tag`
  - `filter_type`
  - `illuminance`
  - `motor2_speed`
  - `volume`

### Air Purifier Pro V7 (zhimi.airpurifier.v7)

- Power (on, off)
- Operation modes (auto, silent, favorite)
- Child lock (on, off)
- LED (on, off)
- Favorite Level (0...16)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `aqi`
  - `mode`
  - `filter_hours_used`
  - `filter_life_remaining`
  - `favorite_level`
  - `child_lock`
  - `led`
  - `motor_speed`
  - `average_aqi`
  - `learn_mode`
  - `extra_features`
  - `turbo_mode_supported`
  - `button_pressed`
  - `filter_rfid_product_id`
  - `filter_rfid_tag`
  - `filter_type`
  - `illuminance`
  - `motor2_speed`
  - `volume`

### Air Purifier 2S (zhimi.airpurifier.mc1)

- Power (on, off)
- Operation modes (auto, silent, favorite)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off)
- Favorite Level (0...16)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `aqi`
  - `mode`
  - `filter_hours_used`
  - `filter_life_remaining`
  - `favorite_level`
  - `child_lock`
  - `led`
  - `motor_speed`
  - `average_aqi`
  - `learn_mode`
  - `extra_features`
  - `turbo_mode_supported`
  - `button_pressed`
  - `filter_rfid_product_id`
  - `filter_rfid_tag`
  - `filter_type`
  - `illuminance`
  - `buzzer`

### Air Purifier 3/3H (2019) (zhimi.airpurifier.ma4/zhimi.airpurifier.mb3)

This model uses newer MiOT communication protocol.

- Power (on, off)
- Operation modes (auto, silent, favorite, fan)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off)
- Favorite Level (0...16)
- Fan Level (1...3)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `aqi`
  - `mode`
  - `filter_hours_used`
  - `filter_life_remaining`
  - `favorite_level`
  - `child_lock`
  - `led`
  - `motor_speed`
  - `average_aqi`
  - `purify_volume`
  - `use_time`
  - `buzzer`
  - `led_brightness`
  - `filter_rfid_product_id`
  - `filter_rfid_tag`
  - `filter_type`
  - `fan_level`

### Air Purifier V3 (zhimi.airpurifier.v3)

- Power (on, off)
- Operation modes (auto, silent, favorite, idle, medium, high, strong)
- Child lock (on, off)
- LED (on, off)
- Attributes
  - `model`
  - `aqi`
  - `mode`
  - `led`
  - `buzzer`
  - `child_lock`
  - `illuminance`
  - `filter_hours_used`
  - `filter_life_remaining`
  - `motor_speed`
  - `average_aqi`
  - `volume`
  - `motor2_speed`
  - `filter_rfid_product_id`
  - `filter_rfid_tag`
  - `filter_type`
  - `purify_volume`
  - `learn_mode`
  - `sleep_time`
  - `sleep_mode_learn_count`
  - `extra_features`
  - `auto_detect`
  - `use_time`
  - `button_pressed`

### Air Humidifier (zhimi.humidifier.v1)

- On, Off
- Operation modes (silent, medium, high, strong)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off), LED brightness (bright, dim, off)
- Target humidity (30, 40, 50, 60, 70, 80)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `mode`
  - `buzzer`
  - `child_lock`
  - `trans_level`
  - `target_humidity`
  - `led_brightness`
  - `button_pressed`
  - `use_time`
  - `hardware_version`

### Air Humidifier CA (zhimi.humidifier.ca1)

- On, Off
- Operation modes (silent, medium, high, auto)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off), LED brightness (bright, dim, off)
- Target humidity (30, 40, 50, 60, 70, 80)
- Dry mode (on, off)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `mode`
  - `buzzer`
  - `child_lock`
  - `trans_level`
  - `target_humidity`
  - `led_brightness`
  - `button_pressed`
  - `use_time`
  - `hardware_version`
  - `motor_speed`
  - `depth`
  - `dry`

### Air Humidifier CA4 (zhimi.humidifier.ca4)

- On, Off
- Operation modes (auto, low, mid, high)
- Buzzer (on, off)
- Child lock (on, off)
- LED brightness (off, dim, bright)
- Target humidity (30 - 80)
- Dry mode (on, off)
- Motor speed rpm (200 - 2000)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `mode`
  - `buzzer`
  - `child_lock`
  - `target_humidity`
  - `led_brightness`
  - `use_time`
  - `actual_speed`
  - `button_pressed`
  - `dry`
  - `fahrenheit`
  - `motor_speed`
  - `power_time`
  - `water_level`

### Air Humidifier CB (zhimi.humidifier.cb1)

- On, Off
- Operation modes (silent, medium, high, auto)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off), LED brightness (bright, dim, off)
- Target humidity (30, 40, 50, 60, 70, 80)
- Dry mode (on, off)
- Attributes
  - `speed`
  - `speed_list`
  - `model`
  - `temperature`
  - `humidity`
  - `mode`
  - `buzzer`
  - `child_lock`
  - `target_humidity`
  - `led_brightness`
  - `use_time`
  - `hardware_version`
  - `motor_speed`
  - `depth`
  - `dry`
  - `supported_features`

### Zero Fog Humidifier (shuii.humidifier.jsq001)

- Power (on, off)
- Operation modes (Intelligent, Level1, Level2, Level3, Level4)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off), LED brightness (high, low, off)
- Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `mode`
  - `buzzer`
  - `child_lock`
  - `led`
  - `led_brightness`
  - `no_water`
  - `lid_opened`

### Air Fresh VA2

- Power (on, off)
- Operation modes (auto, silent, interval, low, middle, strong)
- Buzzer (on, off)
- Child lock (on, off)
- LED (on, off), LED brightness (bright, dim, off)
- Attributes
  - `model`
  - `aqi`
  - `average_aqi`
  - `temperature`
  - `humidity`
  - `co2`
  - `mode`
  - `led`
  - `led_brightness`
  - `buzzer`
  - `child_lock`
  - `filter_life_remaining`
  - `filter_hours_used`
  - `use_time`
  - `motor_speed`
  - `extra_features`


### Air Humidifier MJJSQ and JSQ1 (deerma.humidifier.mjjsq, deerma.humidifier.jsq1)

* Power (on, off)
* Operation modes (low, medium, high, humidity)
* Buzzer (on, off)
* LED (on, off)
* Target humidity (0...99)
* Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `mode`
  - `buzzer`
  - `target_humidity`
  - `led`
  - `no_water`
  - `water_tank_detached`

### Air Dehumidifier (nwt.derh.wdh318efw1)

* HVAC mode (dry, off)
* Preset mode (on, auto, dryCloth)
* Target humidity (40, 50, 60)
* Fan mode (sleep, low, medium, high, strong)
* Buzzer (on, off)
* Child lock (on, off)
* LED (on, off)
* Attributes
  - `model`
  - `temperature`
  - `humidity`
  - `mode`
  - `buzzer`
  - `child_lock`
  - `target_humidity`
  - `led`
  - `fan_speed`
  - `tank_full`
  - `compressor_status`
  - `defrost_status`
  - `fan_st`
  - `alarm`


### Pedestal Fan

* Power (on, off)
* Speed levels (Level 1, Level 2, Level 3, Level 4)
* Oscillate (on, off)
* Oscillation angle (30, 60, 90, 120)
* Natural mode (on, off)
* Rotate by 5 degrees (left, right)
* Child lock (on, off)
* LED brightness (bright, dim, off)
* Attributes
  - `model`
  - `temperature` (zhimi.fan.v2 and v3 only)
  - `humidity` (zhimi.fan.v2 and v3 only)
  - `led_brightness`
  - `buzzer`
  - `child_lock`
  - `natural_level`
  - `oscillate`
  - `delay_off_countdown`
  - `speed`
  - `direct_speed`
  - `natural_speed`
  - `angle`
  - `use_time`
  - `ac_power`
  - `battery` (zhimi.fan.v2 and v3 only)
  - `battery_charge` (zhimi.fan.v2 & v3 only)
  - `button_pressed` (zhimi.fan.v2 & v3 only)
  - `led` (zhimi.fan.v2 only)
  - `battery_state` (zhimi.fan.v2 only)


## Install

You can install this custom component by adding this repository ([https://github.com/syssi/xiaomi_airpurifier](https://github.com/syssi/xiaomi_airpurifier/)) to [HACS](https://hacs.xyz/) in the settings menu of HACS first. You will find the custom component in the integration menu afterwards, look for 'Xiaomi Mi Air Purifier and Xiaomi Mi Air Humidifier Integration'. Alternatively, you can install it manually by copying the custom_component folder to your Home Assistant configuration folder.


## Setup

```yaml
# configuration.yaml

fan:
  - platform: xiaomi_miio_airpurifier
    name: Xiaomi Air Purifier 2
    host: 192.168.130.71
    token: b7c4a758c251955d2c24b1d9e41ce47d
    model: zhimi.airpurifier.m1

  - platform: xiaomi_miio_airpurifier
    name: Xiaomi Air Purifier Pro
    host: 192.168.130.73
    token: 70924d6fa4b2d745185fa4660703a5c0
    model: zhimi.airpurifier.v6

  - platform: xiaomi_miio_airpurifier
    name: Xiaomi Air Humidifier
    host: 192.168.130.72
    token: 2b00042f7481c7b056c4b410d28f33cf
    model: zhimi.humidifier.v1

  - platform: xiaomi_miio_airpurifier
    name: Xiaomi Air Fresh
    host: 192.168.130.74
    token: 91d89cf53c4090f4c653174f6737102f
    model: zhimi.airfresh.va2

  - platform: xiaomi_miio_airpurifier
    name: Xiaomi Smart Fan
    host: 192.168.130.75
    token: b7c4a758c251955d2c24b1d9e41ce4ff

climate:
  - platform: xiaomi_miio_airpurifier
    name: Xiaomi Air Dehumidifier
    host: 192.168.130.76
    token: 86c4c41dc7af0e0520e170c8a1f92f62
```

Configuration variables:
- **host** (*Required*): The IP of your light.
- **token** (*Required*): The API token of your light.
- **name** (*Optional*): The name of your light.
- **model** (*Optional*): The model of your device. This setting can be used to bypass the device model detection and is recommended if your device isn't always available.

## Template sensor example

If your entity has another name the value `xiaomi_air_purifier` and `xiaomi_air_humidifier` must be updated.

```
# configuration.yaml

sensor:
  - platform: template
    sensors:
      airpurifier_aqi:
        friendly_name: Air Purifier Air Quality Index
        value_template: '{{ states.fan.xiaomi_air_purifier.attributes.aqi }}'
      airpurifier_temperature:
        friendly_name: Air Purifier Temperature
        value_template: '{{ states.fan.xiaomi_air_purifier.attributes.temperature }}'
        unit_of_measurement: '°C'
      airpurifier_humidity:
        friendly_name: Air Purifier Humidity
        value_template: '{{ states.fan.xiaomi_air_purifier.attributes.humidity }}'
        unit_of_measurement: '%'

      airhumidifier_temperature:
        friendly_name: Air Humidifier Temperature
        value_template: '{{ states.fan.xiaomi_air_humidifier.attributes.temperature }}'
        unit_of_measurement: '°C'
      airhumidifier_humidity:
        friendly_name: Air Humidifier Humidity
        value_template: '{{ states.fan.xiaomi_air_humidifier.attributes.humidity }}'
        unit_of_measurement: '%'
```

## Platform services

#### Service `fan.set_speed`

Set the fan speed/operation mode.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                       |
| `speed`                   |       no | Fan speed. Valid values are 'Auto', 'Silent', 'Favorite' and 'Idle'. Valid values of the Pedestal Fan are `Level 1`, `Level 2`, `Level 3` and `Level 4` as well as a value between 0 and 100. |

#### Service `xiaomi_miio_airpurifier.fan_set_buzzer_on` (Air Purifier Pro excluded)

Turn the buzzer on.

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.        |

#### Service `xiaomi_miio_airpurifier.fan_set_buzzer_off` (Air Purifier Pro excluded)

Turn the buzzer off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_led_on` (Air Purifier only)

Turn the led on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_led_off` (Air Purifier only)

Turn the led off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_child_lock_on`

Turn the child lock on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_child_lock_off`

Turn the child lock off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier._fan_set_delay_off`

Set the scheduled turn off time. Supported values are 0, 60, 120, 180, 240, 300, 360, 420, 480 minutes. When 0 is passed, delay_off is disabled.

| Service data attribute    | Optional | Description                                                                                                          |
|---------------------------|----------|----------------------------------------------------------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                                                                       |
| `delay_off_countdown`     |       no | Time in minutes. Valid values are `0`, `60`, `120`, `180`, `240`, `300`, `240`, `300`, `360`, `420`, `480` minutes.  |

#### Service `xiaomi_miio_airpurifier.fan_set_led_brightness` (Air Purifier Pro excluded)

Set the led brightness. Supported values are 0 (Bright), 1 (Dim), 2 (Off).

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |
| `brightness`              |       no | Brightness, between 0 and 2.                            |

#### Service `xiaomi_miio_airpurifier.fan_set_favorite_level` (Air Purifier only)

Set the favorite level of the operation mode "favorite".

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |
| `level`                   |       no | Level, between 0 and 16.                                |

#### Service `xiaomi_miio_airpurifier.fan_set_auto_detect_on` (Air Purifier Pro only)

Turn the auto detect on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_auto_detect_off` (Air Purifier Pro only)

Turn the auto detect off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_learn_mode_on` (Air Purifier 2 only)

Turn the learn mode on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_learn_mode_off` (Air Purifier 2 only)

Turn the learn mode off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_volume` (Air Purifier Pro only)

Set the sound volume.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |
| `volume`                  |       no | Volume, between 0 and 100.                              |

#### Service `xiaomi_miio_airpurifier.fan_reset_filter` (Air Purifier 2 and Air Fresh only)

Reset the filter lifetime and usage.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_extra_features` (Air Purifier and Air Fresh only)

Set the extra features.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |
| `features`                |       no | Integer, known values are 0 and 1.                      |

#### Service `xiaomi_miio_airpurifier.fan_set_target_humidity` (Air Humidifier only)

Set the target humidity.

| Service data attribute    | Optional | Description                                                     |
|---------------------------|----------|-----------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                  |
| `humidity`                |       no | Target humidity. The allowed values varies by model.            |

#### Service `xiaomi_miio_airpurifier.fan_set_dry_on` (Air Humidifier CA only)

Turn the dry mode on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `xiaomi_miio_airpurifier.fan_set_dry_off` (Air Humidifier CA only)

Turn the dry mode off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.          |

#### Service `fan.oscillate` (Pedestal Fan only)

Oscillates the fan.

| Service data attribute    | Optional | Description                                                           |
|---------------------------|----------|-----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                        |
| `oscillating`             |       no | Flag to turn on/off oscillation. Valid values are `True` and `False`. |

#### Service `fan.set_direction` (Pedestal Fan only)

Rotates the fan 5 degrees to the left/right.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                       |
| `direction`               |       no | Rotate the fan 5 degrees. Valid values are `left` and `right`.       |

#### Service `xiaomi_miio_airpurifier.fan_set_oscillation_angle` (Pedestal Fan only)

Set the oscillation angle. Supported values are 30, 60, 90 and 120 degrees.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                       |
| `angle`                   |       no | Angle in degrees. Valid values are `30`, `60`, `90` and `120`.       |

#### Service `xiaomi_miio_airpurifier.fan_set_natural_mode_on` (Pedestal Fan only)

Turn the natural mode on.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                       |

#### Service `xiaomi_miio_airpurifier.fan_set_natural_mode_off` (Pedestal Fan only)

Turn the natural mode off.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                       |

### Service `xiaomi_miio.fan_set_motor_speed` (Air Humidifier CA4)

Set motor speed RPM.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                       |
| `motor_speed`             |       no | Motor speed RPM. Allowed values are between 200 and 2000             |

#### Service `xiaomi_miio.fan_set_fan_level` (Air Purifier 3H only)

Set the level when on fan mode

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |       no | Only act on a specific Xiaomi miIO fan entity.                       |
| `level`                   |       no | Valid values are `1`, `2` and `3`.                                   |

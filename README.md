# Xiaomi Mi Air Purifier & Xiaomi Mi Air Humidifier

This is a custom component for home assistant to integrate the Xiaomi Mi Air Purifier 2, Air Purifier 2S, Air Purifier Pro, Air Humidifier and Air Fresh.

Please follow the instructions on [Retrieving the Access Token](https://home-assistant.io/components/xiaomi/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

Credits: Thanks to [Rytilahti](https://github.com/rytilahti/python-miio) for all the work.

## Features

### Air Purifier 2

* Power (on, off)
* Operation modes (auto, silent, favorite, idle)
* Buzzer (on, off)
* Child lock (on, off)
* LED (on, off), LED brightness (bright, dim, off)
* Favorite Level (0...16)
* Attributes
  - model
  - temperature
  - humidity
  - aqi
  - mode
  - filter_hours_used
  - filter_life_remaining
  - favorite_level
  - child_lock
  - led
  - motor_speed
  - average_aqi
  - purify_volume
  - learn_mode
  - sleep_time
  - sleep_mode_learn_count
  - extra_features
  - turbo_mode_supported
  - auto_detect
  - use_time
  - button_pressed
  - buzzer
  - led_brightness
  - sleep_mode


### Air Purifier Pro

* Power (on, off)
* Operation modes (auto, silent, favorite)
* Child lock (on, off)
* LED (on, off)
* Favorite Level (0...16)
* Attributes
  - model
  - temperature
  - humidity
  - aqi
  - mode
  - filter_hours_used
  - filter_life_remaining
  - favorite_level
  - child_lock
  - led
  - motor_speed
  - average_aqi
  - purify_volume
  - learn_mode
  - sleep_time
  - sleep_mode_learn_count
  - extra_features
  - turbo_mode_supported
  - auto_detect
  - use_time
  - button_pressed
  - filter_rfid_product_id
  - filter_rfid_tag
  - filter_type
  - illuminance
  - motor2_speed
  - volume

### Air Purifier 3

* Power (on, off)
* Operation modes (auto, silent, favorite, idle, medium, high, strong)
* Child lock (on, off)
* LED (on, off)
* Attributes
  - model
  - aqi
  - mode
  - led
  - buzzer
  - child_lock
  - illuminance
  - filter_hours_used
  - filter_life_remaining
  - motor_speed
  - average_aqi
  - volume
  - motor2_speed
  - filter_rfid_product_id
  - filter_rfid_tag
  - filter_type
  - purify_volume
  - learn_mode
  - sleep_time
  - sleep_mode_learn_count
  - extra_features
  - auto_detect
  - use_time
  - button_pressed

### Air Humidifier

* On, Off
* Operation modes (silent, medium, high)
* Buzzer (on, off)
* Child lock (on, off)
* LED brightness (bright, dim, off)
* Target humidity (30, 40, 50, 60, 70, 80)
* Attributes
  - model
  - temperature
  - humidity
  - mode
  - buzzer
  - child_lock
  - trans_level
  - target_humidity
  - led_brightness
  - button_pressed
  - use_time
  - hardware_version

### Air Humidifier CA

* On, Off
* Operation modes (silent, medium, high, auto)
* Buzzer (on, off)
* Child lock (on, off)
* LED brightness (bright, dim, off)
* Target humidity (30, 40, 50, 60, 70, 80)
* Dry mode (on, off)
* Attributes
  - model
  - temperature
  - humidity
  - mode
  - buzzer
  - child_lock
  - trans_level
  - target_humidity
  - led_brightness
  - button_pressed
  - use_time
  - hardware_version
  - speed
  - depth
  - dry

### Air Fresh VA2

* Power (on, off)
* Operation modes (auto, silent, interval, low, middle, strong)
* Buzzer (on, off)
* Child lock (on, off)
* LED (on, off), LED brightness (bright, dim, off)
* Attributes
  - model
  - aqi
  - average_aqi
  - temperature
  - humidity
  - co2
  - mode
  - led
  - led_brightness
  - buzzer
  - child_lock
  - filter_life_remaining
  - filter_hours_used
  - use_time
  - motor_speed
  - extra_features


## Setup

```yaml
# configuration.yaml

fan:
  - platform: xiaomi_miio
    name: Xiaomi Air Purifier 2
    host: 192.168.130.71
    token: b7c4a758c251955d2c24b1d9e41ce47d
    model: zhimi.airpurifier.m1

  - platform: xiaomi_miio
    name: Xiaomi Air Purifier Pro
    host: 192.168.130.73
    token: 70924d6fa4b2d745185fa4660703a5c0
    model: zhimi.airpurifier.v6

  - platform: xiaomi_miio
    name: Xiaomi Air Humidifier
    host: 192.168.130.72
    token: 2b00042f7481c7b056c4b410d28f33cf
    model: zhimi.humidifier.v1

  - platform: xiaomi_miio
    name: Xiaomi Air Fresh
    host: 192.168.130.74
    token: 91d89cf53c4090f4c653174f6737102f
    model: zhimi.airfresh.va2
```

Configuration variables:
- **host** (*Required*): The IP of your light.
- **token** (*Required*): The API token of your light.
- **name** (*Optional*): The name of your light.
- **model** (*Optional*): The model of your device. Valid values are `zhimi.airpurifier.m1`, `zhimi.airpurifier.m2`, `zhimi.airpurifier.ma1`, `zhimi.airpurifier.ma2`, `zhimi.airpurifier.sa1`, `zhimi.airpurifier.sa2`, `zhimi.airpurifier.v1`, `zhimi.airpurifier.v2`, `zhimi.airpurifier.v3`, `zhimi.airpurifier.v5`, `zhimi.airpurifier.v6`, `zhimi.humidifier.v1`, `zhimi.humidifier.ca1` and `zhimi.airfresh.va2`. This setting can be used to bypass the device model detection and is recommended if your device isn't always available.

## Platform services

#### Service `fan.set_speed`

Set the fan speed/operation mode.

| Service data attribute    | Optional | Description                                                          |
|---------------------------|----------|----------------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.               |
| `speed`                   |       no | Fan speed. Valid values are 'Auto', 'Silent', 'Favorite' and 'Idle'. |

#### Service `fan.xiaomi_miio_set_buzzer_on` (Air Purifier Pro excluded)

Turn the buzzer on.

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_buzzer_off` (Air Purifier Pro excluded)

Turn the buzzer off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_led_on` (Air Purifier only)

Turn the led on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_led_off` (Air Purifier only)

Turn the led off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_child_lock_on`

Turn the child lock on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_child_lock_off`

Turn the child lock off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_led_brightness` (Air Purifier Pro excluded)

Set the led brightness. Supported values are 0 (Bright), 1 (Dim), 2 (Off).

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |
| `brightness`              |       no | Brightness, between 0 and 2.                            |

#### Service `fan.xiaomi_miio_set_favorite_level` (Air Purifier only)

Set the favorite level of the operation mode "favorite".

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |
| `level`                   |       no | Level, between 0 and 16.                                |

#### Service `fan.xiaomi_miio_set_auto_detect_on` (Air Purifier Pro only)

Turn the auto detect on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_auto_detect_off` (Air Purifier Pro only)

Turn the auto detect off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_learn_mode_on` (Air Purifier 2 only)

Turn the learn mode on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_learn_mode_off` (Air Purifier 2 only)

Turn the learn mode off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_volume` (Air Purifier Pro only)

Set the sound volume.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |
| `volume`                  |       no | Volume, between 0 and 100.                              |

#### Service `fan.xiaomi_miio_reset_filter` (Air Purifier 2 and Air Fresh only)

Reset the filter lifetime and usage.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_extra_features` (Air Purifier and Air Fresh only)

Set the extra features.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |
| `features`                |       no | Integer, known values are 0 and 1.                      |

#### Service `fan.xiaomi_miio_set_target_humidity` (Air Humidifier only)

Set the target humidity.

| Service data attribute    | Optional | Description                                                     |
|---------------------------|----------|-----------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.          |
| `humidity`                |       no | Target humidity. Allowed values are 30, 40, 50, 60, 70 and 80   |

#### Service `fan.xiaomi_miio_set_dry_on` (Air Humidifier CA only)

Turn the dry mode on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service `fan.xiaomi_miio_set_dry_off` (Air Humidifier CA only)

Turn the dry mode off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

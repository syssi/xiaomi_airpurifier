# Xiaomi Air Purifier

This is a custom component for home assistant to integrate the Xiaomi Air Purifier 2.

Please follow the instructions on [Retrieving the Access Token](https://home-assistant.io/components/xiaomi/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

Credits: Thanks to [Rytilahti](https://github.com/rytilahti/python-mirobo) for all the work.

## Features
* On, Off
* Operation modes (auto, silent, favorite, idle)
* Buzzer (on, off)
* LED (on, off), LED brightness (bright, dim, off)
* Favorite Level
* States
  - power
  - aqi
  - humidity
  - temperature
  - mode
  - led
  - led_brightness
  - buzzer
  - child_lock
  - brightness
  - favorite_level
  - filter1_life
  - f1_hour_used
  - use_time
  - motor1_speed

## Setup

```yaml
# confugration.yaml

fan:
  - platform: xiaomi_airpurifier
    name: Xiaomi Air Purifier 2
    host: 192.168.130.71
    token: b7c4a758c251955d2c24b1d9e41ce47d
```

## Platform services

#### Service airpurifier/set_buzzer_on

Turn the buzzer on.

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on specific air purifier. Else targets all.  |

#### Service airpurifier/set_buzzer_off

Turn the buzzer off.

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on specific air purifier. Else targets all.  |

#### Service airpurifier/set_led_on

Turn the led on.

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on specific air purifier. Else targets all.  |

#### Service airpurifier/set_led_off

Turn the led off.

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on specific air purifier. Else targets all.  |

#### Service airpurifier/set_led_brightness

Set the led brightness. Supported values are 0 (Bright), 1 (Dim), 2 (Off).

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on specific air purifier. Else targets all.  |
| `brightness`              |       no | Brightness, between 0 and 2.                          |

#### Service airpurifier/set_favorite_level

Set the favorite level of the operation mode "favorite".

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on specific air purifier. Else targets all.  |
| `level`                   |       no |  Level, between 0 and 17.                             |


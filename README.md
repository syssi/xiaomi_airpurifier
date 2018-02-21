# Xiaomi Mi Air Purifier & Xiaomi Mi Air Humidifier

This is a custom component for home assistant to integrate the Xiaomi Mi Air Purifier 2, Air Purifier 2S, Air Purifier Pro and Air Humidifier.

Please follow the instructions on [Retrieving the Access Token](https://home-assistant.io/components/xiaomi/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

Credits: Thanks to [Rytilahti](https://github.com/rytilahti/python-miio) for all the work.

## Features

### Air Purifier

* On, Off
* Operation modes (auto, silent, favorite, idle)
* Buzzer (on, off)
* Child lock (on, off)
* LED (on, off), LED brightness (bright, dim, off)
* Favorite Level (0...16)
* Attributes
  - power
  - aqi
  - average_aqi
  - humidity
  - temperature
  - mode
  - favorite_level
  - led
  - led_brightness
  - buzzer
  - child_lock
  - purify_volume
  - filter_life_remaining
  - filter_hours_used
  - motor_speed

### Air Humidifier

* On, Off
* Operation modes (silent, medium, high)
* Buzzer (on, off)
* Child lock (on, off)
* LED brightness (bright, dim, off)
* Target humidity (30, 40, 50, 60, 70, 80)
* Attributes
  - power
  - humidity
  - temperature
  - mode
  - led_brightness
  - buzzer
  - child_lock
  - trans_level
  - target_humidity

## Setup

```yaml
# confugration.yaml

fan:
  - platform: xiaomi_miio
    name: Xiaomi Air Purifier
    host: 192.168.130.71
    token: b7c4a758c251955d2c24b1d9e41ce47d

  - platform: xiaomi_miio
    name: Xiaomi Air Humidifier
    host: 192.168.130.72
    token: 2b00042f7481c7b056c4b410d28f33cf
```

## Platform services

#### Service fan/xiaomi_miio_set_buzzer_on

Turn the buzzer on.

| Service data attribute    | Optional | Description                                           |
|---------------------------|----------|-------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service fan/xiaomi_miio_set_buzzer_off

Turn the buzzer off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service fan/xiaomi_miio_set_led_on

Turn the led on. (Air Purifier only)

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service fan/xiaomi_miio_set_led_off

Turn the led off. (Air Purifier only)

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service fan/xiaomi_miio_set_child_lock_on

Turn the child lock on.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service fan/xiaomi_miio_set_child_lock_off

Turn the child lock off.

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |

#### Service fan/xiaomi_miio_set_led_brightness

Set the led brightness. Supported values are 0 (Bright), 1 (Dim), 2 (Off).

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |
| `brightness`              |       no | Brightness, between 0 and 2.                            |

#### Service fan/xiaomi_miio_set_favorite_level

Set the favorite level of the operation mode "favorite". (Air Purifier only)

| Service data attribute    | Optional | Description                                             |
|---------------------------|----------|---------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.  |
| `level`                   |       no | Level, between 0 and 16.                                |

#### Service fan/xiaomi_miio_set_target_humidity

Set the target humidity. (Air Humidifier only)

| Service data attribute    | Optional | Description                                                     |
|---------------------------|----------|-----------------------------------------------------------------|
| `entity_id`               |      yes | Only act on a specific air purifier. Else targets all.          |
| `humidity`                |       no | Target humidity. Allowed values are 30, 40, 50, 60, 70 and 80   |

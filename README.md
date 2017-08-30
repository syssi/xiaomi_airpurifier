# xiaomi air purifier

Initial integration of Xiaomi Air Purifier 2.

Thanks to [Rytilahti](https://github.com/rytilahti/python-mirobo) for all the work.

Please follow the instructions on [Retrieving the Access Token](https://home-assistant.io/components/xiaomi/#retrieving-the-access-token) to get the API token to use in the configuration.yaml file.

# Setup

```
fan:
  - platform: xiaomi_airpurifier
    name: Xiaomi Air Purifier 2
    host: 192.168.130.71
    token: b7c4a758c251955d2c24b1d9e41ce47d
```

# Features
* Basic functionality: on, off, operation modes (auto, silent, favorite, idle) & current state

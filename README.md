## Control of Mitsubishi SRK20ZM-S via Broadling IR for Home Assistant
A small project for my Broadlink IR and Mitsubishi ACs for Home Assistant. You may use it as a base for other ACs if Broadlink IR is used.

### Installation
Copy folder `mitsubishi` to `/config/custom_components`. 
Include following in `configuration.yaml`:
```
mitsubishi:
  ip_address: !secret broadlink_living_room_ip
```

### Configuration attributes
- `ip_address` - **mandatory** IP address of corresponding Broablink IR device.
- `name` - friendly name.
- `temperature_entity` - separate unrelated temperature sensor entity, which will be used as part of climate entity (for observability in google home for example). For example if you have xiaomi bluetooth sensor in the room where AC is located, then measured temperature will be also visible in newly created climate entity as part of AC and will be accessible from google.
- `humidity_entity` - separate unrelated humidity sensor entity, which will be used as part of climate entity (for observability in google home for example). For example if you have xiaomi bluetooth sensor in the room where AC is located, then measured humidity will be also visible in newly created climate entity as part of AC and will be accessible from google.

### Configuration saving issues
Integration saves wanted configuration in JSON file located under `/config/custom_components/mitsubishi/json/` so no need for input_select or input_number entities. It might happen that due to not found folder `json` configuration shall not be saved. To solve it, simply create `json` folder under `/config/custom_components/mitsubishi` and set rights for everyone to be able to modify contents of this folder. After first request to change data files with corresponding friendly names shall be created.

### configuration.yaml entry example
```
mitsubishi:
  - ip_address: !secret broadlink_living_room_ip
    name: "Living Room"
    temperature_entity: "sensor.living_room_temperature"
    humidity_entity: "sensor.living_room_humidity"
  - ip_address: !secret broadlink_bedroom_ip
    name: "Bedroom"
    temperature_entity: "sensor.bedroom_temperature"
    humidity_entity: "sensor.bedroom_humidity"
```

### Afternote
You are free to use or modify this software, but i do not take any responsibility for any issues.

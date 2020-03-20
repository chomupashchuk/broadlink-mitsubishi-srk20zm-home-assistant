## Control of Mitsubishi SRK20ZM-S via Broadling IR for Home Assistant
A small project for my Broadlink IR and Mitsubishi ACs for Home Assistant. You may use it as a base for other ACs if Broadlink IR is used.

### Configuration.yaml example
```
mitsubishi:
  - ip_address: !secret broadlink_living_room_ip
    name: "Living Room"
    temperature_entity: "sensor.living_room_temperature"
    humidity_entity: "sensor.living_room_humidity"
```

#import requests
import neohubapi.neohub as neohub
from .config import Config

_TRUE_STRINGS = {"TRUE", "ON", "1", "ACTIVE", "HOLD", "ENABLED", "YES"}
_FALSE_STRINGS = {"FALSE", "OFF", "0", "INACTIVE", "NONE", ""}


def _coerce_bool(value):
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in _TRUE_STRINGS:
            return True
        if normalized in _FALSE_STRINGS:
            return False
    return bool(value)

hub = neohub.NeoHub(port=4243, token=Config.NEOHUB_TOKEN)

async def get_device_status(device_name):
    hub_data = await hub.get_devices_data()
    devices = hub_data['neo_devices']
    for device in devices:
        if device.name == device_name:
            print(f"Temperature in zone {device.name}: {device.temperature}")            
            device_data = {
                "is_hold": False, #TODO
                "current": device.temperature,
                "target": device.target_temperature,
                "standby": device.standby
            }
            return device_data, device

async def set_temperature(device, temp):
    return await hub.set_target_temperature(temp,[device])

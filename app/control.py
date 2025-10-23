import time, datetime
from .config import Config
from .octopus_api import get_current_price
from .neohub_api import get_device_status, set_temperature
from .logic import should_preheat, decide_temperature

state = {
    "last_temp": None,
    "last_price": None,
    "manual_override": False,
    "standby": False,
    "status": "Starting...",
    "preheat_active": False,
    "last_update": None,
    "current_temp": None
}

async def control_loop():
    while True:
        try:
            price = get_current_price()
            device_info, device = await get_device_status(Config.DEVICE_NAME)

            state["manual_override"] = device_info["is_hold"]
            state["standby"] = device_info["standby"]
            state["current_temp"] = device_info["current"]
            preheat = should_preheat()

            if device_info["standby"]:
                msg = "Thermostat in standby — skipping update."
                print(msg)
            elif device_info["is_hold"]:
                msg = "Manual override active — skipping update."
                print(msg)
            else:
                new_temp = decide_temperature(price, state["last_temp"], state["last_price"], preheat)
                if new_temp != state["last_temp"]:
                    await set_temperature(device, new_temp)
                    msg = f"Price {price:.2f}p → set {Config.DEVICE_NAME} to {new_temp}°C {'(preheat)' if preheat else ''}"
                    state["last_temp"] = new_temp
                else:
                    msg = f"Price {price:.2f}p → hold {state['last_temp']}°C"
                print(msg)

            state.update({
                "status": msg,
                "last_update": datetime.datetime.now(),
                "last_price": price,
                "preheat_active": preheat
            })

        except Exception as e:
            msg = f"Error: {e}"
            print(msg)
            state["status"] = msg

        time.sleep(Config.INTERVAL)

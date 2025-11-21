import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OCTOPUS_PRODUCT = os.getenv("OCTOPUS_PRODUCT")
    OCTOPUS_TARIFF = os.getenv("OCTOPUS_TARIFF")
    NEOHUB_TOKEN= os.getenv("NEOHUB_TOKEN")
    DEVICE_NAME = os.getenv("DEVICE_NAME")
    INTERVAL = int(os.getenv("INTERVAL", 900))
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8080))

    LOW_PRICE = float(os.getenv("LOW_PRICE", 15))
    LOW_PRICE_2 = float(os.getenv("LOW_PRICE_2", 20))
    MID_PRICE = float(os.getenv("MID_PRICE", 25))
    MID_PRICE_2 = float(os.getenv("MID_PRICE_2", 30))
    TEMP_LOW = float(os.getenv("TEMP_LOW", 23))
    TEMP_LOW_2 = float(os.getenv("TEMP_LOW_2", 25))
    TEMP_MID = float(os.getenv("TEMP_MID", 27))
    TEMP_MID_2 = float(os.getenv("TEMP_MID_2", 29))
    TEMP_HIGH = float(os.getenv("TEMP_HIGH", 30))

    TEMP_HYSTERESIS = float(os.getenv("TEMP_HYSTERESIS", 0.5))
    PRICE_HYSTERESIS = float(os.getenv("PRICE_HYSTERESIS", 2))

    PREHEAT_LOOKAHEAD_HOURS = float(os.getenv("PREHEAT_LOOKAHEAD_HOURS", 2))
    PREHEAT_THRESHOLD = float(os.getenv("PREHEAT_THRESHOLD", 18))
    PREHEAT_FORECAST_WINDOW = float(os.getenv("PREHEAT_FORECAST_WINDOW", 6))

    QUIET_START = os.getenv("QUIET_START", "22:30")
    QUIET_END = os.getenv("QUIET_END", "04:00")

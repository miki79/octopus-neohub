import requests, datetime
from .config import Config

OCTOPUS_URL = (
    f"https://api.octopus.energy/v1/products/{Config.OCTOPUS_PRODUCT}/"
    f"electricity-tariffs/{Config.OCTOPUS_TARIFF}/standard-unit-rates/"
)

def fetch_prices():
    """Return full list of Agile prices."""
    r = requests.get(OCTOPUS_URL, timeout=10)
    r.raise_for_status()
    return r.json()["results"]

def get_current_price():
    """Return the current half-hour price."""
    now = datetime.datetime.now(datetime.timezone.utc)
    for p in fetch_prices():        
        start = datetime.datetime.fromisoformat(p["valid_from"].replace("Z","+00:00"))
        end = datetime.datetime.fromisoformat(p["valid_to"].replace("Z","+00:00"))
        if start <= now < end:

            return p["value_inc_vat"]
    return None

def get_forecast_prices(hours=Config.PREHEAT_FORECAST_WINDOW):
    """Return upcoming prices for the forecast window."""
    now = datetime.datetime.now(datetime.timezone.utc)
    window = now + datetime.timedelta(hours=hours)
    return [
        p for p in fetch_prices()
        if datetime.datetime.fromisoformat(p["valid_from"].replace("Z","+00:00")) < window
    ]

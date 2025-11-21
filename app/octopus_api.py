import aiohttp
import datetime
from .config import Config

OCTOPUS_URL = (
    f"https://api.octopus.energy/v1/products/{Config.OCTOPUS_PRODUCT}/"
    f"electricity-tariffs/{Config.OCTOPUS_TARIFF}/standard-unit-rates/"
)

_price_cache = None
_cache_expiry = None

async def fetch_prices():
    """Return full list of Agile prices, with caching."""
    global _price_cache, _cache_expiry
    now = datetime.datetime.now(datetime.timezone.utc)

    if _price_cache is None or _cache_expiry is None or now >= _cache_expiry:
        async with aiohttp.ClientSession() as session:
            async with session.get(OCTOPUS_URL, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                
        # Parse dates once and cache
        _price_cache = []
        for p in data["results"]:
            p["valid_from_dt"] = datetime.datetime.fromisoformat(p["valid_from"].replace("Z", "+00:00"))
            p["valid_to_dt"] = datetime.datetime.fromisoformat(p["valid_to"].replace("Z", "+00:00"))
            _price_cache.append(p)
            
        _cache_expiry = now + datetime.timedelta(minutes=30)

    return _price_cache

async def get_current_price():
    """Return the current half-hour price."""
    now = datetime.datetime.now(datetime.timezone.utc)
    prices = await fetch_prices()
    for p in prices:        
        if p["valid_from_dt"] <= now < p["valid_to_dt"]:
            return p["value_inc_vat"]
    return None

async def get_forecast_prices(hours=Config.PREHEAT_FORECAST_WINDOW):
    """Return upcoming prices for the forecast window."""
    now = datetime.datetime.now(datetime.timezone.utc)
    window = now + datetime.timedelta(hours=hours)
    prices = await fetch_prices()
    return [
        p for p in prices
        if p["valid_from_dt"] < window
    ]

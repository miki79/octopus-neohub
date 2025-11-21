import datetime
from zoneinfo import ZoneInfo
from .config import Config
from .octopus_api import get_forecast_prices

# --- Caching for Forecast Prices ---
_forecast_cache = None
_forecast_last_updated = None
CACHE_EXPIRY_SECONDS = 1800  # 30 minutes

async def get_cached_forecast():
    """
    Returns cached forecast prices if available and not expired.
    Otherwise, fetches new data and updates the cache.
    """
    global _forecast_cache, _forecast_last_updated
    now = datetime.datetime.now(datetime.timezone.utc)

    if _forecast_cache and _forecast_last_updated and (now - _forecast_last_updated).total_seconds() < CACHE_EXPIRY_SECONDS:
        return _forecast_cache

    forecast = await get_forecast_prices()
    if forecast:
        _forecast_cache = forecast
        _forecast_last_updated = now
    return forecast

# --- Price Configuration ---
# Price bands: (price_threshold, temperature)
PRICE_BANDS = sorted([
    (Config.LOW_PRICE, Config.TEMP_HIGH),
    (Config.LOW_PRICE_2, Config.TEMP_MID_2),
    (Config.MID_PRICE, Config.TEMP_MID),
    (Config.MID_PRICE_2, Config.TEMP_LOW_2),
], key=lambda x: x[0])

# --- Core Logic Functions ---
async def should_preheat(current_price):
    """
    Forecast-based preheating logic.

    - Looks ahead for a defined number of hours.
    - If the average price in the future is significantly higher than the current price,
      and the current price is below a specific threshold, activate preheating.
    """
    if current_price is None:
        return False

    forecast = await get_cached_forecast()
    if not forecast:
        return False

    now = datetime.datetime.now(datetime.timezone.utc)
    lookahead_time = now + datetime.timedelta(hours=Config.PREHEAT_LOOKAHEAD_HOURS)

    future_prices = [
        p["value_inc_vat"]
        for p in forecast
        if now < p["valid_from_dt"] <= lookahead_time
    ]

    if not future_prices:
        return False

    avg_future_price = sum(future_prices) / len(future_prices)

    # Conditions for preheating
    is_expensive_later = avg_future_price > current_price * 1.2  # e.g., 20% more expensive
    is_cheap_now = current_price <= Config.PREHEAT_THRESHOLD

    return is_cheap_now and is_expensive_later

def decide_temperature(price, last_temp, last_price, preheat_active):
    """
    Determines the target temperature based on price, preheating status, and hysteresis.
    """
    if preheat_active:
        target_temp = Config.TEMP_HIGH
    else:
        # Default to the lowest temperature
        target_temp = Config.TEMP_LOW
        # Find the correct temperature from the price bands
        for price_threshold, temp in PRICE_BANDS:
            if price < price_threshold:
                target_temp = temp
                break

    # Enforce quiet hours to avoid high temperatures overnight
    now_uk = datetime.datetime.now(ZoneInfo("Europe/London"))
    current_time_str = now_uk.strftime("%H:%M")
    
    # Simple string comparison works for 24h format if intervals don't cross midnight in a complex way
    # But to be safe and handle crossing midnight (e.g. 22:30 to 04:00), we should parse.
    # However, for simplicity and since we have strings in config:
    
    q_start = datetime.datetime.strptime(Config.QUIET_START, "%H:%M").time()
    q_end = datetime.datetime.strptime(Config.QUIET_END, "%H:%M").time()
    current_time = now_uk.time()

    is_quiet = False
    if q_start <= q_end:
        is_quiet = q_start <= current_time <= q_end
    else: # Crosses midnight
        is_quiet = current_time >= q_start or current_time <= q_end

    if is_quiet and target_temp > Config.TEMP_MID:
        target_temp = Config.TEMP_MID

    # Apply hysteresis to prevent rapid switching
    # 1. If price change is insignificant, keep the last temperature.
    if last_price is not None and last_temp is not None and abs(price - last_price) < Config.PRICE_HYSTERESIS:
        return last_temp
    # 2. If the new target temperature is only slightly different, keep the last temperature.
    if last_temp is not None and abs(target_temp - last_temp) < Config.TEMP_HYSTERESIS:
        return last_temp

    return target_temp

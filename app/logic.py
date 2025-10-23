import datetime
from zoneinfo import ZoneInfo
from .config import Config
from .octopus_api import get_forecast_prices, get_current_price

def should_preheat():
    """
    Forecast-based preheating:
    - Look ahead PREHEAT_LOOKAHEAD_HOURS.
    - If future prices will exceed current by > threshold,
      and current price <= PREHEAT_THRESHOLD → preheat now.
    """
    current = get_current_price()
    if current is None:
        return False

    forecast = get_forecast_prices()
    lookahead = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=Config.PREHEAT_LOOKAHEAD_HOURS)
    
    future_prices = [
        p["value_inc_vat"]
        for p in forecast
        if datetime.datetime.fromisoformat(p["valid_from"].replace("Z","+00:00")) <= lookahead
    ]
    if not future_prices:
        return False

    avg_future = sum(future_prices) / len(future_prices)
    expensive_ahead = avg_future > Config.MID_PRICE
    cheap_now = current <= Config.PREHEAT_THRESHOLD
    return cheap_now and expensive_ahead

def decide_temperature(price, last_temp, last_price, preheat_active):
    """Apply hysteresis and preheating logic."""
    if preheat_active:
        target = Config.TEMP_HIGH
    elif price < Config.LOW_PRICE:
        target = Config.TEMP_HIGH
    elif price < Config.LOW_PRICE_2:
        target = Config.TEMP_MID_2    
    elif price < Config.MID_PRICE:
        target = Config.TEMP_MID
    elif price < Config.MID_PRICE_2:
        target = Config.TEMP_MID_2
    else:
        target = Config.TEMP_LOW

    now_uk = datetime.datetime.now(ZoneInfo("Europe/London"))
    current_time = now_uk.time()
    quiet_hours = current_time >= datetime.time(22, 30) or current_time < datetime.time(4, 0)
    if quiet_hours and target > Config.TEMP_MID:
        target = Config.TEMP_MID

    # Apply hysteresis
    if last_temp is not None and abs(target - last_temp) < Config.TEMP_HYSTERESIS:
        target = last_temp
    if last_price is not None and abs(price - last_price) < Config.PRICE_HYSTERESIS:
        target = last_temp or target

    return target

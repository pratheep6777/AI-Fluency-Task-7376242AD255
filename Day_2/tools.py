"""
tools.py

Small "tool" functions the ReAct agent can call.

I used local/mocked data instead of a real weather API and a real forex
API. Reasons:
  1. No internet access in the environment I built/tested this in.
  2. It keeps the project fully runnable and reproducible for grading
     without needing anyone to sign up for API keys just to see the
     tool-calling part work.

The important bit for this assignment isn't "is the data live", it's
"does the agent decide it needs external info, call a function to get
it, and use the result" -- which this still demonstrates fine. Swapping
these for requests.get(real_api_url) later is a 5 minute change.
"""

_WEATHER_DB = {
    "tokyo": {
        "temp_c": 14,
        "condition": "light rain",
        "weekend_forecast": "rain expected on both Sat and Sun, ~70% chance",
    },
    "paris": {"temp_c": 9, "condition": "cloudy", "weekend_forecast": "dry, partly cloudy"},
    "delhi": {"temp_c": 31, "condition": "clear sky", "weekend_forecast": "clear, hot"},
}

# snapshot rates, NOT live
_FX_RATES = {
    ("usd", "jpy"): 149.85,
    ("usd", "eur"): 0.92,
    ("usd", "inr"): 83.10,
}


def get_weather(city: str) -> dict:
    city = city.strip().lower()
    print(f"    -> [TOOL] get_weather(city='{city}') called")
    data = _WEATHER_DB.get(city)
    if not data:
        return {"error": f"no weather data cached for '{city}'"}
    return data


def get_exchange_rate(base: str, target: str) -> dict:
    base, target = base.strip().lower(), target.strip().lower()
    print(f"    -> [TOOL] get_exchange_rate(base='{base}', target='{target}') called")
    rate = _FX_RATES.get((base, target))
    if rate is None:
        return {"error": f"no rate cached for {base}->{target}"}
    return {"base": base, "target": target, "rate": rate}

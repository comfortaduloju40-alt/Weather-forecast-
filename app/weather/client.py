"""
Thin wrapper around the OpenWeatherMap APIs: geocoding, current weather,
and 5-day/3-hour forecast (aggregated into daily summaries).
"""

from collections import defaultdict
from datetime import datetime

import requests

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

_GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


class WeatherError(RuntimeError):
    pass


def geocode_city(city_name: str) -> dict:
    resp = requests.get(
        _GEO_URL,
        params={"q": city_name, "limit": 1, "appid": settings.OPENWEATHER_API_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise WeatherError(f"Couldn't find a location called '{city_name}'.")
    place = results[0]
    return {
        "lat": place["lat"],
        "lon": place["lon"],
        "name": place.get("name", city_name),
        "country": place.get("country", ""),
    }


def get_current(lat: float, lon: float) -> dict:
    resp = requests.get(
        _CURRENT_URL,
        params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY, "units": settings.UNITS},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def get_5day_forecast(lat: float, lon: float) -> list[dict]:
    """
    Returns one summary dict per day (up to 5 days) with min/max temp
    and the most common condition, aggregated from 3-hour data points.
    """
    resp = requests.get(
        _FORECAST_URL,
        params={"lat": lat, "lon": lon, "appid": settings.OPENWEATHER_API_KEY, "units": settings.UNITS},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    by_day = defaultdict(list)
    for entry in data.get("list", []):
        day = datetime.fromtimestamp(entry["dt"]).date()
        by_day[day].append(entry)

    summaries = []
    for day, entries in list(by_day.items())[:5]:
        temps = [e["main"]["temp"] for e in entries]
        conditions = [e["weather"][0]["description"] for e in entries]
        # pick the condition closest to midday as the representative one
        midday_entry = min(entries, key=lambda e: abs(datetime.fromtimestamp(e["dt"]).hour - 13))
        summaries.append(
            {
                "date": day,
                "temp_min": min(temps),
                "temp_max": max(temps),
                "condition": midday_entry["weather"][0]["description"],
            }
        )
    return summaries


def unit_symbol() -> str:
    return {"metric": "°C", "imperial": "°F", "standard": "K"}.get(settings.UNITS, "°C")

"""
Handles both input methods: typed city name and shared GPS location.
Formats and sends the current weather + 5-day forecast.
"""

from telegram import Update
from telegram.ext import ContextTypes

from app.logger import get_logger
from app.weather.client import WeatherError, geocode_city, get_5day_forecast, get_current, unit_symbol

logger = get_logger(__name__)


def _format_report(place_name: str, current: dict, forecast: list[dict]) -> str:
    unit = unit_symbol()
    temp = round(current["main"]["temp"])
    feels_like = round(current["main"]["feels_like"])
    condition = current["weather"][0]["description"].capitalize()
    humidity = current["main"]["humidity"]
    wind = current["wind"]["speed"]

    lines = [
        f"*Weather in {place_name}*",
        "",
        f"🌡️ {temp}{unit} (feels like {feels_like}{unit})",
        f"☁️ {condition}",
        f"💧 Humidity: {humidity}%",
        f"💨 Wind: {wind} m/s",
        "",
        "*5-day forecast:*",
    ]
    for day in forecast:
        lines.append(
            f"• {day['date'].strftime('%a %d %b')}: "
            f"{round(day['temp_min'])}–{round(day['temp_max'])}{unit}, "
            f"{day['condition']}"
        )
    return "\n".join(lines)


async def _send_weather(update: Update, lat: float, lon: float, place_name: str) -> None:
    try:
        current = get_current(lat, lon)
        forecast = get_5day_forecast(lat, lon)
    except WeatherError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return
    except Exception:
        logger.exception("Weather API call failed")
        await update.message.reply_text("⚠️ Couldn't fetch weather right now. Please try again shortly.")
        return

    report = _format_report(place_name, current, forecast)
    await update.message.reply_text(report, parse_mode="Markdown")


async def handle_city_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city_name = update.message.text.strip()
    try:
        place = geocode_city(city_name)
    except WeatherError as exc:
        await update.message.reply_text(f"⚠️ {exc}")
        return
    except Exception:
        logger.exception("Geocoding failed")
        await update.message.reply_text("⚠️ Couldn't look up that location right now.")
        return

    display_name = f"{place['name']}, {place['country']}" if place["country"] else place["name"]
    await _send_weather(update, place["lat"], place["lon"], display_name)


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    loc = update.message.location
    await _send_weather(update, loc.latitude, loc.longitude, "your location")

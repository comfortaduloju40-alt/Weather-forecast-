"""
/start and /help command handlers.
"""

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

_HELP_TEXT = (
    "👋 I'll give you the current weather and a 5-day forecast.\n\n"
    "• Type a city name (e.g. `London` or `Lagos, NG`)\n"
    "• Or tap the button below to share your location"
)


def _location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Share my location", request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_HELP_TEXT, parse_mode="Markdown", reply_markup=_location_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_HELP_TEXT, parse_mode="Markdown", reply_markup=_location_keyboard())


"""
Registers every command/message handler on the Application.
"""

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.handlers.start import start_command, help_command
from app.handlers.weather import handle_city_text, handle_location


def register_handlers(app: Application) -> None:
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city_text))

"""
Central place for environment-driven configuration.
"""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: os.environ["BOT_TOKEN"])
    OPENWEATHER_API_KEY: str = field(default_factory=lambda: os.environ["OPENWEATHER_API_KEY"])
    UNITS: str = field(default_factory=lambda: os.environ.get("UNITS", "metric"))
    WEBHOOK_URL: str = field(default_factory=lambda: os.environ.get("WEBHOOK_URL", ""))
    PORT: int = field(default_factory=lambda: int(os.environ.get("PORT", "8080")))
    LOG_LEVEL: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))


settings = Settings()

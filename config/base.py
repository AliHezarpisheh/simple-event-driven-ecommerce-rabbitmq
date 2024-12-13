"""Module for defining base configurations."""

from .logging import LoggingConfig
from .settings import Settings

# Logging
logger = LoggingConfig().get_logger()

# Settings
settings = Settings()  # type: ignore

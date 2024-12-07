"""Module for defining base configurations."""

from .logging import LoggingConfig

# Logging
logger = LoggingConfig().get_logger()

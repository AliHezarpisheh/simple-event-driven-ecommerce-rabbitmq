"""Module for defining base configurations."""

from .logging import LoggingConfig
from .rabbitmq import AsyncRabbitmqManager
from .settings import Settings

# Logging
logger = LoggingConfig().get_logger()

# Settings
settings = Settings()  # type: ignore

# RabbitMQ
rabbitmq_manager = AsyncRabbitmqManager(amqp_url=settings.AMQP_URL)

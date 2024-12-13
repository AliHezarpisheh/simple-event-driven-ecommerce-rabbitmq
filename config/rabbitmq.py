"""Module holding RabbitMQ management components."""

from aio_pika import RobustChannel, RobustConnection, connect_robust


class AsyncRabbitmqManager:
    """Async rabbitmq manager class."""  # TODO: Improve docstring.

    def __init__(self, amqp_url: str) -> None:
        """Initialize the `AsyncRabbitmqManager` with the given AMQP URL."""
        self._amqp_url = amqp_url
        self._connection: RobustConnection | None = None
        self._channel: RobustChannel | None = None

    async def get_connection(self) -> RobustConnection:
        """Create a connection."""  # TODO: Improve docstring.
        if not self._connection:
            self._connection = await connect_robust(self._amqp_url)
        return self._connection

    async def get_channel(self) -> RobustChannel:
        """Create a channel."""  # TODO: Improve docstring.
        if not self._connection:
            connection = await self.get_connection()

        if not self._channel:
            self._channel = connection.channel()
        return self._channel

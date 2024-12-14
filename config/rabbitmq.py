"""Module holding RabbitMQ management components."""

from aio_pika import ExchangeType, connect_robust
from aio_pika.abc import (
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
    AbstractRobustQueue,
)


class AsyncRabbitmqManager:
    """Async rabbitmq manager class."""

    def __init__(self, amqp_url: str) -> None:
        """Initialize an `AsyncRabbitmqManager` object."""
        self._amqp_url = amqp_url
        self._connection: AbstractRobustConnection | None = None
        self._channel: AbstractRobustChannel | None = None

    async def get_connection(self) -> AbstractRobustConnection:
        """
        Get a connection to RabbitMQ.

        Establishes and returns a robust connection to RabbitMQ, connecting to
        the URL provided during initialization.

        Returns
        -------
        AbstractRobustConnection
            The connection to the RabbitMQ server.
        """
        if not self._connection:
            self._connection = await connect_robust(self._amqp_url)
        return self._connection

    async def get_channel(self) -> AbstractRobustChannel:
        """
        Get a channel from the RabbitMQ connection.

        Establishes a channel if one does not exist and returns it. The channel
        is used for performing RabbitMQ operations.

        Returns
        -------
        AbstractRobustChannel
            The channel for interacting with RabbitMQ.
        """
        connection = await self.get_connection()

        if not self._channel:
            self._channel = await connection.channel()

        return self._channel

    async def declare_exchange(
        self,
        name: str,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
        durable: bool = True,
        auto_delete: bool = False,
    ) -> AbstractRobustExchange:
        """
        Declare an exchange on RabbitMQ.

        Declares an exchange with the specified parameters on the RabbitMQ server.

        Parameters
        ----------
        name : str
            The name of the exchange to declare.
        exchange_type : ExchangeType, optional
            The type of the exchange (default is `ExchangeType.DIRECT`).
        durable : bool, optional
            Whether the exchange should survive server restarts (default is True).
        auto_delete : bool, optional
            Whether the exchange should be deleted when no consumers are connected
            (default is False).

        Returns
        -------
        AbstractRobustExchange
            The declared exchange.
        """
        channel = await self.get_channel()
        exchange = await channel.declare_exchange(
            name=name, type=exchange_type, durable=durable, auto_delete=auto_delete
        )
        return exchange

    async def declare_queue(
        self,
        name: str,
        durable: bool = True,
        auto_delete: bool = False,
        dead_letter_exchange: str | None = None,
    ) -> AbstractRobustQueue:
        """
        Declare a queue on RabbitMQ.

        Declares a queue with the specified parameters on the RabbitMQ server.

        Parameters
        ----------
        name : str
            The name of the queue to declare.
        durable : bool, optional
            Whether the queue should survive server restarts (default is True).
        auto_delete : bool, optional
            Whether the queue should be deleted when no consumers are connected
            (default is False).
        dead_letter_exchange : str, optional
            The name of the dead letter exchange to use for the queue (default is None).

        Returns
        -------
        AbstractRobustQueue
            The declared queue.
        """
        channel = await self.get_channel()
        arguments = (
            {"x-dead-letter-exchange": dead_letter_exchange}
            if dead_letter_exchange
            else {}
        )
        queue = await channel.declare_queue(
            name=name, durable=durable, auto_delete=auto_delete, arguments=arguments
        )
        return queue

    async def bind_queue(
        self,
        exchange: AbstractRobustExchange,
        queue: AbstractRobustQueue,
        routing_key: str = "",
    ) -> None:
        """
        Bind a queue to an exchange.

        Binds a queue to an exchange with an optional routing key.

        Parameters
        ----------
        exchange : AbstractRobustExchange
            The exchange to bind the queue to.
        queue : AbstractRobustQueue
            The queue to bind.
        routing_key : str, optional
            The routing key to use for binding (default is an empty string).
        """
        await queue.bind(exchange=exchange, routing_key=routing_key)

    async def close(self) -> None:
        """
        Close the RabbitMQ connection and channel.

        Closes the active RabbitMQ connection and channel, if they are open.
        """
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

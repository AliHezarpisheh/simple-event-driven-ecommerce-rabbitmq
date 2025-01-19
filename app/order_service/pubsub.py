"""Module contains a superclass for order producers and consumers."""

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractExchange

from app.consts import ORDERS_EXCHANGE_NAME
from config.base import AsyncRabbitmqManager


class OrderPubSub:
    """Base class for managing order-related messaging via RabbitMQ."""

    def __init__(self, rabbitmq_manager: AsyncRabbitmqManager) -> None:
        """Instantiate a `OrderPubSub` object."""
        self.rabbitmq_manager = rabbitmq_manager

    async def declare_order_exchange(
        self, channel: AbstractChannel
    ) -> AbstractExchange:
        """
        Declare the 'orders' exchange on the specified channel.

        Parameters
        ----------
        channel : AbstractChannel
            The channel on which to declare the exchange.

        Returns
        -------
        AbstractExchange
            The declared exchange object.
        """
        order_exchange = await self.rabbitmq_manager.declare_exchange(
            channel=channel,
            name=ORDERS_EXCHANGE_NAME,
            exchange_type=ExchangeType.DIRECT,
        )
        return order_exchange

    @staticmethod
    def _get_new_order_routing_key() -> str:
        """
        Retrieve the routing key for new order messages.

        Returns
        -------
        str
            The routing key for new orders, typically 'orders.new'.
        """
        return "orders.new"

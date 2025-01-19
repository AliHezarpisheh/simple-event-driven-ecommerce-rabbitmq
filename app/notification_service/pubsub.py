"""Module contains a subclass for order producers and consumers."""

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractExchange

from app.consts import NOTIFICATION_EXCHANGE_NAME
from config.base import AsyncRabbitmqManager


class NotificationPubSub:
    """Base class for managing notification-related messaging via RabbitMQ."""

    def __init__(self, rabbitmq_manager: AsyncRabbitmqManager) -> None:
        """Instantiate a `NotificationPubSub` object."""
        self.rabbitmq_manager = rabbitmq_manager

    async def declare_notification_exchange(
        self, channel: AbstractChannel
    ) -> AbstractExchange:
        """
        Declare the 'notifications' exchange on the specified channel.

        Parameters
        ----------
        channel : AbstractChannel
            The channel on which to declare the exchange.

        Returns
        -------
        AbstractExchange
            The declared exchange object.
        """
        notification_exchange = await self.rabbitmq_manager.declare_exchange(
            channel=channel,
            name=NOTIFICATION_EXCHANGE_NAME,
            exchange_type=ExchangeType.FANOUT,
        )
        return notification_exchange

    @staticmethod
    def _get_notification_routing_key() -> str:
        """
        Retrieve the routing key for notifications.

        Returns
        -------
        str
            The routing key for notifications. The routing key will be ignored because
            of the FANOUT exchange type.
        """
        return "notifications"

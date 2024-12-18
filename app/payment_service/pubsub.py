"""Module contains a subclass for payment producers and consumers."""

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractQueue

from app.consts import (
    FAILED_PAYMENTS_QUEUE_NAME,
    PAYMENTS_EXCHANGE_NAME,
    SUCCESS_PAYMENTS_QUEUE_NAME,
)
from config.base import AsyncRabbitmqManager


class PaymentPubSub:
    """Base class for managing payment-related messaging via RabbitMQ."""

    def __init__(self, rabbitmq_manager: AsyncRabbitmqManager) -> None:
        """Instantiate a `PaymentPubSub` object."""
        self.rabbitmq_manager = rabbitmq_manager

    async def declare_payments_exchange(
        self, channel: AbstractChannel
    ) -> AbstractExchange:
        """
        Declare the 'payments' exchange on the specified channel.

        Parameters
        ----------
        channel : AbstractChannel
            The channel on which to declare the exchange.

        Returns
        -------
        AbstractExchange
            The declared exchange object.
        """
        payments_exchange = await self.rabbitmq_manager.declare_exchange(
            channel=channel,
            name=PAYMENTS_EXCHANGE_NAME,
            exchange_type=ExchangeType.DIRECT,
        )
        return payments_exchange

    async def declare_success_payments_queue(
        self, channel: AbstractChannel
    ) -> AbstractQueue:
        """
        Declare the 'success_payments' queue on the specified channel.

        Parameters
        ----------
        channel : AbstractChannel
            The channel on which to declare the queue.

        Returns
        -------
        AbstractQueue
            The declared queue object.
        """
        success_payments_queue = await self.rabbitmq_manager.declare_queue(
            channel=channel,
            name=SUCCESS_PAYMENTS_QUEUE_NAME,
        )
        return success_payments_queue

    async def declare_failed_payments_queue(
        self, channel: AbstractChannel
    ) -> AbstractQueue:
        """
        Declare the 'failed_payments' queue on the specified channel.

        Parameters
        ----------
        channel : AbstractChannel
            The channel on which to declare the queue.

        Returns
        -------
        AbstractQueue
            The declared queue object.
        """
        failed_payments_queue = await self.rabbitmq_manager.declare_queue(
            channel=channel,
            name=FAILED_PAYMENTS_QUEUE_NAME,
        )
        return failed_payments_queue

    @staticmethod
    def _get_success_payment_routing_key() -> str:
        """
        Retrieve the routing key for successful payments.

        Returns
        -------
        str
            The routing key for successful payment, typically 'payment.success'.
        """
        return "payment.success"

    @staticmethod
    def _get_failed_payment_routing_key() -> str:
        """
        Retrieve the routing key for failed payments.

        Returns
        -------
        str
            The routing key for failed payment, typically 'payment.success'.
        """
        return "payment.failed"

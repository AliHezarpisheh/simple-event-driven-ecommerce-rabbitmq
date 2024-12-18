"""Handles the publishing of new order messages to a RabbitMQ exchange."""

import asyncio
from decimal import Decimal

from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractExchange

from app.consts import ORDER_EXCHANGE_NAME
from config.base import AsyncRabbitmqManager, logger, rabbitmq_manager

from .schemas import OutgoingOrder


class OrderProducer:
    """Produce and publish new order messages to a RabbitMQ exchange."""

    def __init__(self, rabbitmq_manager: AsyncRabbitmqManager) -> None:
        """Initialize an `OrderProduce` object."""
        self.rabbitmq_manager = rabbitmq_manager

    async def produce_new_order(self, order: OutgoingOrder) -> None:
        """
        Publish an order message to a RabbitMQ exchange.

        Parameters
        ----------
        order : Order
            The order object to be serialized and published.
        """
        async with await self.rabbitmq_manager.get_connection() as connection:
            logger.info("Opening connection and channel to publish order...")
            channel = await self.rabbitmq_manager.get_channel(connection)

            order_exchange = await self.declare_order_exchange(channel=channel)

            message = Message(
                body=order.to_message(),
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            publish_result = await order_exchange.publish(
                message=message, routing_key=self._get_new_order_routing_key()
            )
            logger.info(
                "Published order to the %s exchange with the result: %s",
                ORDER_EXCHANGE_NAME,
                publish_result.name,
            )

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
            name=ORDER_EXCHANGE_NAME,
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


if __name__ == "__main__":
    order = OutgoingOrder(
        customer_id=12,
        items=["fruits", "vegetables"],
        total_price=Decimal(120),
        status="created",
    )
    order_producer = OrderProducer(rabbitmq_manager=rabbitmq_manager)
    asyncio.run(order_producer.produce_new_order(order=order))

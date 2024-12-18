"""Handles the consuming of new order messages from a RabbitMQ queue."""

import asyncio
import json

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractIncomingMessage

from app.consts import ORDER_EXCHANGE_NAME, ORDER_QUEUE_NAME
from app.order_service.schemas import IncomingOrder
from config.base import AsyncRabbitmqManager, rabbitmq_manager


class OrderConsumer:
    """Consume and receive new order messages from a RabbitMQ queue."""

    def __init__(self, rabbitmq_manager: AsyncRabbitmqManager) -> None:
        """Initialize an `OrderConsumer` object."""
        self.rabbitmq_manager = rabbitmq_manager

    async def consume_new_order(self) -> None:
        """
        Consume new order messages from the RabbitMQ queue.

        This method establishes a connection with RabbitMQ, declares the necessary
        exchange and queue, binds the queue to the exchange with the appropriate
        routing key, and starts consuming messages. The consumer will process
        incoming messages by calling the `on_new_order_message` method.
        """
        async with await self.rabbitmq_manager.get_connection() as connection:
            channel = await self.rabbitmq_manager.get_channel(connection)
            await self.rabbitmq_manager.set_qos(channel=channel, prefetch_count=100)

            order_exchange = await self.declare_order_exchange(channel=channel)

            order_queue = await self.rabbitmq_manager.declare_queue(
                channel=channel,
                name=ORDER_QUEUE_NAME,
            )
            await order_queue.bind(
                order_exchange, routing_key=self._get_new_order_binding_key()
            )
            await order_queue.consume(self.on_new_order_message)

            await asyncio.Future()

    async def on_new_order_message(self, message: AbstractIncomingMessage) -> None:
        """
        Process a new order message.

        This method is called when a new order message is received.

        Parameters
        ----------
        message : AbstractIncomingMessage
            The message received from the RabbitMQ queue to be processed.
        """
        async with message.process():
            order = IncomingOrder(**json.loads(message.body.decode()))
            print(order)

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
    def _get_new_order_binding_key() -> str:
        """
        Retrieve the routing key for new order messages.

        Returns
        -------
        str
            The routing key for new orders, typically 'orders.new'.
        """
        return "orders.new"


if __name__ == "__main__":
    order_consumer = OrderConsumer(rabbitmq_manager=rabbitmq_manager)
    asyncio.run(order_consumer.consume_new_order())

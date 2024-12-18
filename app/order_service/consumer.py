"""Module handles the consuming of new order messages from a RabbitMQ queue."""

import asyncio
import json
from collections.abc import Awaitable
from typing import Callable

from aio_pika.abc import AbstractIncomingMessage

from app.consts import ORDERS_QUEUE_NAME
from app.order_service.pubsub import OrderPubSub
from app.order_service.schemas import IncomingOrder
from config.base import AsyncRabbitmqManager, rabbitmq_manager

OrderMessageHandler = (
    Callable[[IncomingOrder], None] | Callable[[IncomingOrder], Awaitable[None]]
)


class OrderConsumer(OrderPubSub):
    """Consume and receive new order messages from a RabbitMQ queue."""

    def __init__(self, rabbitmq_manager: AsyncRabbitmqManager) -> None:
        """Initialize an `OrderConsumer` object."""
        self.rabbitmq_manager = rabbitmq_manager

    async def consume_new_order(self, on_message_func: OrderMessageHandler = print) -> None:
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
                name=ORDERS_QUEUE_NAME,
            )
            await order_queue.bind(
                order_exchange, routing_key=self._get_new_order_routing_key()
            )

            async def wrapped_on_message(message: AbstractIncomingMessage) -> None:
                """Wrap `on_new_order_message` to apply `on_message_func`."""
                await self.on_new_order_message(
                    message=message, on_message_func=on_message_func
                )

            await order_queue.consume(wrapped_on_message)

            await asyncio.Future()

    async def on_new_order_message(
        self,
        on_message_func: OrderMessageHandler,
        message: AbstractIncomingMessage,
    ) -> None:
        """
        Process a new order message.

        This method is called when a new order message is received.

        Parameters
        ----------
        on_message_func : Callable[[IncomingOrder], None]
            A callback function to handle the `IncomingOrder` object.
        message : AbstractIncomingMessage
            The message received from the RabbitMQ queue to be processed.
        """
        async with message.process():
            order = IncomingOrder(**json.loads(message.body.decode()))

            if asyncio.iscoroutinefunction(on_message_func):
                await on_message_func(order)
            else:
                on_message_func(order)


if __name__ == "__main__":
    order_consumer = OrderConsumer(rabbitmq_manager=rabbitmq_manager)
    asyncio.run(order_consumer.consume_new_order())

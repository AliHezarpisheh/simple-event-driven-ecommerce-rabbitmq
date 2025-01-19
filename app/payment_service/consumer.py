"""Module handles the consuming of payment messages from a RabbitMQ queue."""

import asyncio
import json
from collections.abc import Awaitable
from typing import Callable

from aio_pika.abc import AbstractIncomingMessage

from app.payment_service.pubsub import PaymentPubSub
from app.payment_service.schemas import IncomingPayment

PaymentMessageHandler = (
    Callable[[IncomingPayment], None] | Callable[[IncomingPayment], Awaitable[None]]
)


class PaymentConsumer(PaymentPubSub):
    """Consume and receive payment messages from a RabbitMQ queue."""

    async def consume_payments(
        self, on_message_func: PaymentMessageHandler = print
    ) -> None:
        """
        Consume payment messages from RabbitMQ queues.

        This method establishes a connection with RabbitMQ, declares the necessary
        exchange and queue, binds the queue to the exchange with the appropriate
        routing key, and starts consuming messages. The consumer will process
        incoming messages by calling the `on_payment_message` method.
        """
        async with await self.rabbitmq_manager.get_connection() as connection:
            channel = await self.rabbitmq_manager.get_channel(connection=connection)

            payment_exchange = await self.declare_payments_exchange(channel=channel)

            success_payment_queue = await self.declare_success_payments_queue(
                channel=channel
            )
            failed_payment_queue = await self.declare_failed_payments_queue(
                channel=channel
            )

            await success_payment_queue.bind(
                exchange=payment_exchange,
                routing_key=self._get_success_payment_routing_key(),
            )
            await failed_payment_queue.bind(
                exchange=payment_exchange,
                routing_key=self._get_failed_payment_routing_key(),
            )

            async def wrapped_on_message(message: AbstractIncomingMessage) -> None:
                """Wrap `on_payment_message` to apply `on_message_func`."""
                await self.on_payment_message(  # pragma: no cover
                    on_message_func=on_message_func, message=message
                )

            await asyncio.gather(
                success_payment_queue.consume(wrapped_on_message),
                failed_payment_queue.consume(wrapped_on_message),
            )
            await asyncio.Future()

    async def on_payment_message(
        self, on_message_func: PaymentMessageHandler, message: AbstractIncomingMessage
    ) -> None:
        """
        Process a payment message.

        This method is called when a payment message is received.

        Parameters
        ----------
        on_message_func : Callable[[IncomingOrder], None]
            A callback function to handle the `IncomingPayment` object.
        message : AbstractIncomingMessage
            The message received from the RabbitMQ queue to be processed.
        """
        async with message.process():
            payment = IncomingPayment(**json.loads(message.body.decode()))

            if asyncio.iscoroutinefunction(on_message_func):
                await on_message_func(payment)
            else:
                on_message_func(payment)

"""Module handles the publishing of new order messages to a RabbitMQ exchange."""

import asyncio
from decimal import Decimal

from aio_pika import DeliveryMode, Message

from app.consts import ORDERS_EXCHANGE_NAME
from app.order_service.pubsub import OrderPubSub
from config.base import logger, rabbitmq_manager

from .schemas import OutgoingOrder


class OrderProducer(OrderPubSub):
    """Produce and publish new order messages to a RabbitMQ exchange."""

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
                ORDERS_EXCHANGE_NAME,
                publish_result,
            )


if __name__ == "__main__":
    order = OutgoingOrder(  # type: ignore
        customer_id=12,
        items=["fruits", "vegetables"],
        total_price=Decimal(120),
        status="created",
    )
    order_producer = OrderProducer(rabbitmq_manager=rabbitmq_manager)
    asyncio.run(order_producer.produce_new_order(order=order))

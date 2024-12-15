"""Handles the publishing of new order messages to a RabbitMQ exchange."""

from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractExchange
from pydantic_core import to_json

from app.consts import ORDER_EXCHANGE_NAME
from config.base import logger, rabbitmq_manager

from .schemas import Order


class OrderProducer:
    """Produce and publish new order messages to a RabbitMQ exchange."""

    async def produce_order(self, order: Order) -> None:
        """
        Publish an order message to a RabbitMQ exchange.

        Parameters
        ----------
        order : Order
            The order object to be serialized and published.
        """
        async with await rabbitmq_manager.get_connection() as connection:
            logger.info("Opening connection and channel to publish order...")
            channel = await rabbitmq_manager.get_channel(connection)

            order_exchange = await self.declare_order_exchange(channel=channel)

            message = Message(
                body=to_json(order),
                delivery_mode=DeliveryMode.PERSISTENT,
            )
            publish_result = await order_exchange.publish(
                message=message, routing_key=self._get_new_order_routing_key()
            )
            logger.info(
                "Published order to the %s exchange with the body: %s",
                ORDER_EXCHANGE_NAME,
                publish_result.body.decode(),  # type: ignore
            )

    @staticmethod
    async def declare_order_exchange(channel: AbstractChannel) -> AbstractExchange:
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
        order_exchange = await rabbitmq_manager.declare_exchange(
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

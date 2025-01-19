"""Module handles the publishing of notification messages to a RabbitMQ exchange."""

import random
from typing import get_args

from aio_pika import DeliveryMode, Message

from app.notification_service.pubsub import NotificationPubSub
from app.notification_service.schemas import Notification, NotificationType
from app.payment_service.schemas import IncomingPayment
from config.base import logger


class NotificationProducer(NotificationPubSub):
    """Produce and publish notification messages to a RabbitMQ exchange."""

    async def produce_notifications(self, payment: IncomingPayment) -> None:
        """
        Produce notification messages to a RabbitMQ exchange.

        Parameters
        ----------
        payment : IncomingPayment
            The incoming payment object containing payment details to create the
            notification object.
        """
        async with await self.rabbitmq_manager.get_connection() as connection:
            channel = await self.rabbitmq_manager.get_channel(connection=connection)

            notifications_exchange = await self.declare_notification_exchange(
                channel=channel
            )

            notification = self._get_notification(payment=payment)
            message = Message(
                body=notification.to_message(),
                delivery_mode=DeliveryMode.PERSISTENT,
            )

            await notifications_exchange.publish(
                message=message, routing_key=self._get_notification_routing_key()
            )
            logger.info("Notification published: %s", notification)

    @staticmethod
    def _get_notification(payment: IncomingPayment) -> Notification:
        """
        Create an `IncomingPayment` object based on the payment data.

        Parameters
        ----------
        payment : IncomingPayment
            The incoming order object containing order details.

        Returns
        -------
        Notification
            The `Notification` object that contains the notification type, recipient,
            and message.
        """
        notification = Notification(
            type=random.choice(get_args(NotificationType)),
            recipient="alihezarpisheh@outlook.com",
            message=(
                f"Your payment status for order {payment.order_id} is: {payment.status}"
            ),
        )
        return notification

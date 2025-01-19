"""Module handles the publishing of new payment messages to a RabbitMQ exchange."""

from aio_pika import DeliveryMode, Message

from app.order_service.schemas import IncomingOrder
from app.payment_service.pubsub import PaymentPubSub
from app.payment_service.schemas import OutgoingPayment
from app.payment_service.utils import is_order_payment_success


class PaymentProducer(PaymentPubSub):
    """Produce and publish payment messages to a RabbitMQ exchange."""

    async def produce_payments(self, order: IncomingOrder) -> None:
        """
        Produce payment messages to a RabbitMQ exchange.

        Parameters
        ----------
        order : IncomingOrder
            The incoming order object containing order details to determine payment
            status.
        """
        async with await self.rabbitmq_manager.get_connection() as connection:
            channel = await self.rabbitmq_manager.get_channel(connection=connection)

            payments_exchange = await self.declare_payments_exchange(channel=channel)

            is_payment_success = is_order_payment_success(order=order)
            payment_routing_key = self._get_payment_routing_key(
                is_payment_success=is_payment_success
            )
            outgoing_payment = self._get_outgoing_payment(
                order=order, is_payment_success=is_payment_success
            )
            message = Message(
                body=outgoing_payment.to_message(),
                delivery_mode=DeliveryMode.PERSISTENT,
            )

            await payments_exchange.publish(
                message=message, routing_key=payment_routing_key
            )

    @staticmethod
    def _get_outgoing_payment(
        order: IncomingOrder, is_payment_success: bool
    ) -> OutgoingPayment:
        """
        Create an `OutgoingPayment` object based on the order's payment success status.

        Parameters
        ----------
        order : IncomingOrder
            The incoming order object containing order details.
        is_payment_success : bool
            A flag indicating whether the payment is successful or failed.

        Returns
        -------
        OutgoingPayment
            The `OutgoingPayment` object that contains the order ID and payment status.
        """
        return OutgoingPayment(  # type: ignore
            order_id=order.order_id,
            status=("success" if is_payment_success else "failed"),
        )

    def _get_payment_routing_key(self, is_payment_success: bool) -> str:
        """
        Get the appropriate routing key for the payment message.

        Parameters
        ----------
        is_payment_success : bool
            A flag indicating whether the payment is successful or failed.

        Returns
        -------
        str
            The routing key for the payment message, either success or failure.
        """
        return (
            self._get_success_payment_routing_key()
            if is_payment_success
            else self._get_failed_payment_routing_key()
        )

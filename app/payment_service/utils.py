"""Module defines utilities for the payment service."""

from app.order_service.schemas import IncomingOrder


def is_order_payment_success(order: IncomingOrder) -> bool:
    """
    Verify the payment of the incoming orders.

    Actually, this is not a `real function`, this project is for RabbitMQ learning
    purposes, and I don't want to implement an actual payment verification system :)
    Consider this function as a mock.

    Parameters
    ----------
    order : IncomingOrder
        The incoming order from the orders.new queue (probably).

    Returns
    -------
    bool
        A boolean value indicating wether the payment was successful or not.
    """
    if order.status == "created":
        return True
    return False

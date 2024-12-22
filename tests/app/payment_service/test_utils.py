"""Test suite for utility functions in the payment service."""

from app.order_service.schemas import IncomingOrder
from app.payment_service.utils import is_order_payment_success


def test_is_order_payment_success(incoming_order: IncomingOrder) -> None:
    """Test for verifying if an order's payment is considered successful."""
    is_success = is_order_payment_success(order=incoming_order)

    assert is_success == (True if incoming_order.status == "created" else False)


def test_is_order_payment_not_success() -> None:
    """Test for verifying if an order's payment is not successful function correctly."""
    incoming_order = IncomingOrder(
        order_id="f01d3c8f-cb0f-4471-9369-50189103da3c",
        customer_id=1,
        items=["orange", "apple"],
        total_price="120",
        status="failed",
        created_at="2024-12-22 12:50:40.659939+00:00",
    )

    is_success = is_order_payment_success(order=incoming_order)

    assert is_success == (True if incoming_order.status == "created" else False)

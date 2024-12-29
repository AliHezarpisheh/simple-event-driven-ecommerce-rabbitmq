"""Conftest file for defining pytest fixtures and configuration for the test suite."""

from decimal import Decimal

import pytest

from app.notification_service.schemas import Notification
from app.order_service.schemas import IncomingOrder, OutgoingOrder
from app.payment_service.schemas import IncomingPayment, OutgoingPayment


@pytest.fixture(scope="session")
def incoming_order() -> IncomingOrder:
    """Return an `IncomingOrder` instance, used in tests."""
    return IncomingOrder(
        order_id="f01d3c8f-cb0f-4471-9369-50189103da3c",
        customer_id=1,
        items=["orange", "apple"],
        total_price="120",
        status="created",
        created_at="2024-12-22 12:50:40.659939+00:00",
    )


@pytest.fixture(scope="session")
def outgoing_order() -> OutgoingOrder:
    """Return an `OutgoingOrder` instance, used in tests."""
    return OutgoingOrder(
        customer_id=1,
        items=["Iphone11", "Asus Vivobook"],
        total_price=Decimal(1999.25),
        status="created",
    )


@pytest.fixture(scope="session")
def incoming_payment() -> IncomingPayment:
    """Return an `IncomingPayment` instance, used in tests."""
    return IncomingPayment(
        payment_id="8eb2a79e-8b95-41dc-a67e-2350a8d326a1",
        order_id="b8095965-1f78-418f-9d36-48fc744a21f6",
        status="success",
        created_at="2024-12-22 12:50:40.659939+00:00",
    )


@pytest.fixture(scope="session")
def outgoing_payment() -> OutgoingPayment:
    """Return an `OutgoingPayment` instance, used in tests."""
    return OutgoingPayment(
        order_id="4572cae5-7af7-44a2-a91c-bf6558fdff1d",
        status="created",
    )


@pytest.fixture(scope="session")
def notification() -> Notification:
    """Return an `Notification` instance, used in tests."""
    return Notification(
        type="email", recipient="test@test.com", message="Notification message."
    )

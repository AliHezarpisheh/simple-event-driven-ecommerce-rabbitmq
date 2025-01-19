"""Test suite for validating `NotificationProducer` class."""

import typing
from unittest import mock

import pytest

from app.notification_service.producer import NotificationProducer
from app.notification_service.schemas import Notification, NotificationType
from app.payment_service.schemas import IncomingPayment
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Fixture for mocking RabbitMQ manager."""
    return mock.AsyncMock(spec_set=AsyncRabbitmqManager)


@pytest.fixture
def notification_producer(
    mock_rabbitmq_manager: mock.AsyncMock,
) -> NotificationProducer:
    """Fixture for initializing `NotificationProducer` instance."""
    return NotificationProducer(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_produce_notifications(
    incoming_payment: IncomingPayment,
    mock_rabbitmq_manager: mock.AsyncMock,
    notification_producer: NotificationProducer,
) -> None:
    """Test producing notifications and publishing to the correct RabbitMQ exchange."""
    # Arrange
    mock_connection = mock.AsyncMock()
    mock_channel = mock.AsyncMock()
    mock_exchange = mock.AsyncMock()
    mock_rabbitmq_manager.get_connection.return_value.__aenter__.return_value = (
        mock_connection
    )
    mock_rabbitmq_manager.get_channel.return_value = mock_channel
    mock_rabbitmq_manager.declare_exchange.return_value = mock_exchange

    # Act
    await notification_producer.produce_notifications(payment=incoming_payment)

    # Assert
    mock_rabbitmq_manager.get_connection.return_value.__aenter__.assert_awaited_once_with()
    mock_rabbitmq_manager.get_channel.assert_awaited_once_with(
        connection=mock_connection
    )
    mock_rabbitmq_manager.declare_exchange.assert_awaited_once()
    mock_exchange.publish.assert_awaited_once()


def test_get_notification(
    incoming_payment: IncomingPayment, notification_producer: NotificationProducer
) -> None:
    """Test getting notification schema."""
    # Act
    notification = notification_producer._get_notification(payment=incoming_payment)

    # Assert
    assert isinstance(notification, Notification)
    assert notification.type in typing.get_args(NotificationType)
    assert notification.message == (
        f"Your payment status for order {incoming_payment.order_id} is: "
        f"{incoming_payment.status}"
    )

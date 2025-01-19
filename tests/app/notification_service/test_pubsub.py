"""Test suite for validating `OrderPubSub` class."""

from unittest import mock

import aio_pika
import pytest

from app.consts import NOTIFICATION_EXCHANGE_NAME
from app.notification_service.pubsub import NotificationPubSub
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Fixture for mocking RabbitMQ manager."""
    return mock.AsyncMock(spec_set=AsyncRabbitmqManager)


@pytest.fixture
def notification_pubsub(mock_rabbitmq_manager: mock.AsyncMock) -> NotificationPubSub:
    """Fixture for initializing `NotificationPubSub` instance."""
    return NotificationPubSub(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_declare_notification_exchange(
    mock_rabbitmq_manager: mock.AsyncMock, notification_pubsub: NotificationPubSub
) -> None:
    """Test declaring notification exchange."""
    # Arrange
    mock_channel = mock.AsyncMock()

    # Act
    await notification_pubsub.declare_notification_exchange(channel=mock_channel)

    # Assert
    mock_rabbitmq_manager.declare_exchange.assert_awaited_once_with(
        channel=mock_channel,
        name=NOTIFICATION_EXCHANGE_NAME,
        exchange_type=aio_pika.ExchangeType.FANOUT,
    )


def test_get_notification_routing_key(notification_pubsub: NotificationPubSub) -> None:
    """Test retrieving notifications routing key."""
    # Act
    routing_key = notification_pubsub._get_notification_routing_key()

    # Assert
    assert routing_key == "notifications"

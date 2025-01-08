"""Test suite for validating `PaymentPubSub` class."""

from unittest import mock

import aio_pika
import pytest

from app.consts import (
    FAILED_PAYMENTS_QUEUE_NAME,
    PAYMENTS_EXCHANGE_NAME,
    SUCCESS_PAYMENTS_QUEUE_NAME,
)
from app.payment_service.pubsub import PaymentPubSub
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Mock an instance of AsyncRabbitmqManager for testing purposes."""
    return mock.AsyncMock(spec_set=AsyncRabbitmqManager)


@pytest.fixture
def payment_pubsub(mock_rabbitmq_manager: mock.AsyncMock) -> PaymentPubSub:
    """Create and return an PaymentPubSub instance using mock_rabbitmq_manager."""
    return PaymentPubSub(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_declare_payment_exchange(
    mock_rabbitmq_manager: mock.AsyncMock, payment_pubsub: PaymentPubSub
) -> None:
    """Test declaring payment exchange."""
    # Arrange
    mock_channel = mock.AsyncMock()

    # Act
    await payment_pubsub.declare_payments_exchange(channel=mock_channel)

    # Assert
    mock_rabbitmq_manager.declare_exchange.assert_awaited_once_with(
        channel=mock_channel,
        name=PAYMENTS_EXCHANGE_NAME,
        exchange_type=aio_pika.ExchangeType.DIRECT,
    )


@pytest.mark.asyncio
async def test_declare_success_payments_queue(
    mock_rabbitmq_manager: mock.AsyncMock, payment_pubsub: PaymentPubSub
) -> None:
    """Test declaring success payments queue."""
    # Arrange
    mock_channel = mock.AsyncMock()

    # Act
    await payment_pubsub.declare_success_payments_queue(channel=mock_channel)

    # Assert
    mock_rabbitmq_manager.declare_queue.assert_awaited_once_with(
        channel=mock_channel, name=SUCCESS_PAYMENTS_QUEUE_NAME
    )


@pytest.mark.asyncio
async def test_declare_failed_payments_queue(
    mock_rabbitmq_manager: mock.AsyncMock, payment_pubsub: PaymentPubSub
) -> None:
    """Test declaring failed payments queue."""
    # Arrange
    mock_channel = mock.AsyncMock()

    # Act
    await payment_pubsub.declare_failed_payments_queue(channel=mock_channel)

    # Assert
    mock_rabbitmq_manager.declare_queue.assert_awaited_once_with(
        channel=mock_channel, name=FAILED_PAYMENTS_QUEUE_NAME
    )


def test_get_success_payment_routing_key(payment_pubsub: PaymentPubSub) -> None:
    """Test retrieving success payment routing key."""
    # Act
    routing_key = payment_pubsub._get_success_payment_routing_key()

    # Assert
    assert routing_key == "payment.success"


def test_get_failed_payment_routing_key(payment_pubsub: PaymentPubSub) -> None:
    """Test retrieving failed payment routing key."""
    # Act
    routing_key = payment_pubsub._get_failed_payment_routing_key()

    # Assert
    assert routing_key == "payment.failed"

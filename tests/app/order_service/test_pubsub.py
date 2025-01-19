"""Test suite for validating `OrderPubSub` class."""

from unittest import mock

import pytest
from aio_pika import ExchangeType

from app.consts import ORDERS_EXCHANGE_NAME
from app.order_service.pubsub import OrderPubSub
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Fixture for mocking RabbitMQ manager."""
    manager = mock.AsyncMock(spec_set=AsyncRabbitmqManager)
    manager.declare_exchange.return_value = mock.AsyncMock()
    return manager


@pytest.fixture
def order_pubsub(mock_rabbitmq_manager: mock.AsyncMock) -> OrderPubSub:
    """Fixture for initializing `OrderPubSub` instance."""
    return OrderPubSub(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_declare_order_exchange(
    order_pubsub: OrderPubSub, mock_rabbitmq_manager: mock.AsyncMock
) -> None:
    """Test declaring order exchange."""
    # Arrange
    mock_channel = mock.AsyncMock()

    # Act
    await order_pubsub.declare_order_exchange(channel=mock_channel)

    # Assert
    mock_rabbitmq_manager.declare_exchange.assert_awaited_once_with(
        channel=mock_channel,
        name=ORDERS_EXCHANGE_NAME,
        exchange_type=ExchangeType.DIRECT,
    )


def test_get_new_order_routing_key(order_pubsub: OrderPubSub) -> None:
    """Test retrieving new order routing key."""
    # Act
    routing_key = order_pubsub._get_new_order_routing_key()

    # Assert
    assert routing_key == "orders.new"

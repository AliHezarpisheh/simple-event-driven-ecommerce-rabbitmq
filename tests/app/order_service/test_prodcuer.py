"""Test suite for validating `OrderProducer` class."""

from unittest import mock

import pytest
from aio_pika import ExchangeType

from app.consts import ORDERS_EXCHANGE_NAME
from app.order_service.producer import OrderProducer
from app.order_service.schemas import OutgoingOrder
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Mock an instance of AsyncRabbitmqManager for testing purposes."""
    return mock.AsyncMock(spec_set=AsyncRabbitmqManager)


@pytest.fixture
def order_producer(mock_rabbitmq_manager: mock.AsyncMock) -> OrderProducer:
    """Create and return an OrderProducer instance using mock_rabbitmq_manager."""
    return OrderProducer(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_produce_new_order(
    outgoing_order: OutgoingOrder,
    mock_rabbitmq_manager: mock.AsyncMock,
    order_producer: OrderProducer,
) -> None:
    """Test the produce_new_order method of the OrderProducer class."""
    # Arrange
    mock_exchange = mock.AsyncMock()
    mock_connection = mock.AsyncMock()
    mock_channel = mock.AsyncMock()
    mock_rabbitmq_manager.declare_exchange.return_value = mock_exchange
    mock_rabbitmq_manager.get_connection.return_value.__aenter__.return_value = (
        mock_connection
    )
    mock_rabbitmq_manager.get_channel.return_value = mock_channel

    # Act
    await order_producer.produce_new_order(order=outgoing_order)

    # Asserts
    mock_rabbitmq_manager.get_connection.return_value.__aenter__.assert_awaited_once()
    mock_rabbitmq_manager.get_channel.assert_awaited_once_with(
        connection=mock_connection
    )
    mock_rabbitmq_manager.declare_exchange.assert_awaited_once_with(
        channel=mock_channel,
        name=ORDERS_EXCHANGE_NAME,
        exchange_type=ExchangeType.DIRECT,
    )
    mock_exchange.publish.assert_awaited_once()

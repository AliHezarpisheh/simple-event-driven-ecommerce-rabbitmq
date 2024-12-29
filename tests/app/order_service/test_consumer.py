"""Test suite for validating `OrderConsumer` class."""

from typing import Any
from unittest import mock

import aio_pika
import pytest

from app.consts import ORDERS_QUEUE_NAME
from app.order_service.consumer import OrderConsumer
from app.order_service.schemas import IncomingOrder
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Mock an instance of AsyncRabbitmqManager for testing purposes."""
    return mock.AsyncMock(spec_set=AsyncRabbitmqManager)


@pytest.fixture
def order_consumer(mock_rabbitmq_manager: mock.AsyncMock) -> OrderConsumer:
    """Create and return an OrderConsumer instance using mock_rabbitmq_manager."""
    return OrderConsumer(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_consume_new_order(
    mock_rabbitmq_manager: mock.AsyncMock, order_consumer: OrderConsumer
) -> None:
    """Test the consume_new_order method of the OrderConsumer class."""
    # Arrange
    mock_connection = mock.AsyncMock()
    mock_channel = mock.AsyncMock()
    mock_exchange = mock.AsyncMock()
    mock_queue = mock.AsyncMock()
    mock_rabbitmq_manager.get_connection.return_value.__aenter__.return_value = (
        mock_connection
    )
    mock_rabbitmq_manager.get_channel.return_value = mock_channel
    mock_rabbitmq_manager.declare_exchange.return_value = mock_exchange
    mock_rabbitmq_manager.declare_queue.return_value = mock_queue

    # Act
    # Mocking `asyncio.Future()` call, preventing the test execution to take for ever.
    with mock.patch(
        "app.order_service.consumer.asyncio.Future", new_callable=mock.AsyncMock
    ):
        await order_consumer.consume_new_order()

    # Assert
    mock_rabbitmq_manager.get_connection.return_value.__aenter__.assert_awaited_once()
    mock_rabbitmq_manager.get_channel.assert_awaited_once_with(
        connection=mock_connection
    )
    mock_rabbitmq_manager.declare_queue.assert_awaited_once_with(
        channel=mock_channel,
        name=ORDERS_QUEUE_NAME,
    )
    mock_queue.bind.assert_awaited_once_with(
        mock_exchange, routing_key=order_consumer._get_new_order_routing_key()
    )
    mock_queue.consume.assert_awaited_once()


@pytest.mark.asyncio
async def test_on_new_order_message_sync(
    capsys: pytest.CaptureFixture[str],
    incoming_order: IncomingOrder,
    order_consumer: OrderConsumer,
) -> None:
    """Test on_new_order_message with a synchronous message handler."""
    # Arrange
    incoming_order_bytes = incoming_order.to_message()
    mock_message = mock.AsyncMock(spec_set=aio_pika.IncomingMessage)
    mock_message.body = incoming_order_bytes

    # Act
    await order_consumer.on_new_order_message(
        on_message_func=print, message=mock_message
    )

    # Asserts
    mock_message.process.return_value.__aenter__.assert_called_once()
    assert str(incoming_order) in capsys.readouterr().out


@pytest.mark.asyncio
async def test_on_new_order_message_async(
    capsys: pytest.CaptureFixture[str],
    incoming_order: IncomingOrder,
    order_consumer: OrderConsumer,
) -> None:
    """Test on_new_order_message with an asynchronous message handler."""
    # Arrange
    incoming_order_bytes = incoming_order.to_message()
    mock_message = mock.AsyncMock(spec_set=aio_pika.IncomingMessage)
    mock_message.body = incoming_order_bytes

    async def async_print(input: Any) -> None:
        print(input)

    # Act
    await order_consumer.on_new_order_message(
        on_message_func=async_print, message=mock_message
    )

    # Asserts
    mock_message.process.return_value.__aenter__.assert_called_once()
    assert str(incoming_order) in capsys.readouterr().out

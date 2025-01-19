"""Test suite for validating `PaymentConsumer` class."""

from typing import Any
from unittest import mock

import aio_pika
import pytest

from app.consts import (
    FAILED_PAYMENTS_QUEUE_NAME,
    PAYMENTS_EXCHANGE_NAME,
    SUCCESS_PAYMENTS_QUEUE_NAME,
)
from app.payment_service.consumer import PaymentConsumer
from app.payment_service.schemas import IncomingPayment
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Mock an instance of AsyncRabbitmqManager for testing purposes."""
    return mock.AsyncMock(spec_set=AsyncRabbitmqManager)


@pytest.fixture
def payment_consumer(mock_rabbitmq_manager: mock.AsyncMock) -> PaymentConsumer:
    """Create and return an PaymentConsumer instance using mock_rabbitmq_manager."""
    return PaymentConsumer(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_consume_payments(
    mock_rabbitmq_manager: mock.AsyncMock, payment_consumer: PaymentConsumer
) -> None:
    """Test consuming payments from RabbitMQ and declaring exchanges and queues."""
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
        "app.payment_service.consumer.asyncio.Future", new_callable=mock.AsyncMock
    ):
        await payment_consumer.consume_payments()

    # Assert
    mock_rabbitmq_manager.get_connection.return_value.__aenter__.assert_awaited_once()
    mock_rabbitmq_manager.get_channel.assert_awaited_once_with(
        connection=mock_connection
    )
    mock_rabbitmq_manager.declare_exchange.assert_awaited_once_with(
        channel=mock_channel,
        name=PAYMENTS_EXCHANGE_NAME,
        exchange_type=aio_pika.ExchangeType.DIRECT,
    )
    declare_queue_calls = [
        mock.call(channel=mock_channel, name=SUCCESS_PAYMENTS_QUEUE_NAME),
        mock.call(channel=mock_channel, name=FAILED_PAYMENTS_QUEUE_NAME),
    ]
    mock_rabbitmq_manager.declare_queue.call_args = declare_queue_calls
    assert mock_queue.bind.await_count == 2


@pytest.mark.asyncio
async def test_on_payment_message_sync(
    capsys: pytest.CaptureFixture[str],
    incoming_payment: IncomingPayment,
    payment_consumer: PaymentConsumer,
) -> None:
    """Test on_payment_message with a synchronous message handler."""
    # Arrange
    incoming_payment_bytes = incoming_payment.to_message()
    mock_message = mock.AsyncMock(spec_set=aio_pika.IncomingMessage)
    mock_message.body = incoming_payment_bytes

    # Act
    await payment_consumer.on_payment_message(
        on_message_func=print, message=mock_message
    )

    # Asserts
    mock_message.process.return_value.__aenter__.assert_called_once()
    assert str(incoming_payment) in capsys.readouterr().out


@pytest.mark.asyncio
async def test_on_payment_message_async(
    capsys: pytest.CaptureFixture[str],
    incoming_payment: IncomingPayment,
    payment_consumer: PaymentConsumer,
) -> None:
    """Test on_payment_message with an asynchronous message handler."""
    # Arrange
    incoming_payment_bytes = incoming_payment.to_message()
    mock_message = mock.AsyncMock(spec_set=aio_pika.IncomingMessage)
    mock_message.body = incoming_payment_bytes

    async def async_print(input: Any) -> None:
        print(input)

    # Act
    await payment_consumer.on_payment_message(
        on_message_func=async_print, message=mock_message
    )

    # Asserts
    mock_message.process.return_value.__aenter__.assert_called_once()
    assert str(incoming_payment) in capsys.readouterr().out

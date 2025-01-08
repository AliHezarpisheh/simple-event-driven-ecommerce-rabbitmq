"""Test suite for validating `PaymentProducer` class."""

import uuid
from datetime import datetime
from unittest import mock

import aio_pika
import pytest

from app.consts import PAYMENTS_EXCHANGE_NAME
from app.order_service.schemas import IncomingOrder
from app.payment_service.producer import PaymentProducer
from app.payment_service.schemas import OutgoingPayment
from config.base import AsyncRabbitmqManager


@pytest.fixture
def mock_rabbitmq_manager() -> mock.AsyncMock:
    """Mock an instance of AsyncRabbitmqManager for testing purposes."""
    return mock.AsyncMock(spec_set=AsyncRabbitmqManager)


@pytest.fixture
def payment_producer(mock_rabbitmq_manager: mock.AsyncMock) -> PaymentProducer:
    """Create and return an PaymentProducer instance using mock_rabbitmq_manager."""
    return PaymentProducer(rabbitmq_manager=mock_rabbitmq_manager)


@pytest.mark.asyncio
async def test_produce_payments(
    mock_rabbitmq_manager: mock.AsyncMock,
    payment_producer: PaymentProducer,
    incoming_order: IncomingOrder,
) -> None:
    """Test producing payments and publishing to the correct RabbitMQ exchange."""
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
    await payment_producer.produce_payments(order=incoming_order)

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
    await mock_exchange.publish.asset_awaited_once()


def test_get_outgoing_success_payment(
    payment_producer: PaymentProducer, incoming_order: IncomingOrder
) -> None:
    """Test generating an outgoing payment for a successful payment."""
    # Act
    outgoing_payment = payment_producer._get_outgoing_payment(
        order=incoming_order, is_payment_success=True
    )

    # Assert
    assert isinstance(outgoing_payment, OutgoingPayment)
    assert outgoing_payment.order_id == incoming_order.order_id
    assert outgoing_payment.status == "success"
    assert isinstance(outgoing_payment.payment_id, uuid.UUID)
    assert isinstance(outgoing_payment.created_at, datetime)


def test_get_outgoing_failed_payment(
    payment_producer: PaymentProducer, incoming_order: IncomingOrder
) -> None:
    """Test generating an outgoing payment for a failed payment."""
    # Act
    outgoing_payment = payment_producer._get_outgoing_payment(
        order=incoming_order, is_payment_success=False
    )

    # Assert
    assert isinstance(outgoing_payment, OutgoingPayment)
    assert outgoing_payment.order_id == incoming_order.order_id
    assert outgoing_payment.status == "failed"
    assert isinstance(outgoing_payment.payment_id, uuid.UUID)
    assert isinstance(outgoing_payment.created_at, datetime)


def test_get_payment_routing_key_success(payment_producer: PaymentProducer) -> None:
    """Test retrieving the routing key for a successful payment."""
    # Act
    actual_routing_key = payment_producer._get_payment_routing_key(
        is_payment_success=True
    )

    # Assert
    expected_routing_key = payment_producer._get_success_payment_routing_key()
    assert actual_routing_key == expected_routing_key


def test_get_payment_routing_key_failed(payment_producer: PaymentProducer) -> None:
    """Test retrieving the routing key for a failed payment."""
    # Act
    actual_routing_key = payment_producer._get_payment_routing_key(
        is_payment_success=False
    )

    # Assert
    expected_routing_key = payment_producer._get_failed_payment_routing_key()
    assert actual_routing_key == expected_routing_key

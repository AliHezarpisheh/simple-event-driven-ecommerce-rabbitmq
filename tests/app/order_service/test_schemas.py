"""Test suite for schema validation functions in the order service."""

from decimal import Decimal

import pytest

from app.order_service.schemas import is_decimal_positive


@pytest.mark.parametrize(
    "expected_number",
    [
        Decimal(0.1),
        Decimal(1),
        Decimal(0.1),
        Decimal(1),
        Decimal(1.0),
        Decimal(2.32),
    ],
)
def test_is_decimal(expected_number: Decimal) -> None:
    """Test for verifying if a decimal number is positive and matches expected value."""
    actual_number = is_decimal_positive(number=expected_number)

    assert actual_number == expected_number


@pytest.mark.parametrize(
    "expected_number",
    [
        Decimal(0),
        Decimal(0.0),
        Decimal(-0.1),
        Decimal(-1.0),
        Decimal(-1),
        Decimal(-2.32),
    ],
)
def test_is_not_decimal(expected_number: Decimal) -> None:
    """Test for ensuring a ValueError is raised for non-positive decimal numbers."""
    with pytest.raises(ValueError, match="The number should be positive"):
        is_decimal_positive(expected_number)

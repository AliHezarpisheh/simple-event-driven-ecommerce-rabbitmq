"""Module defines the schemas and datastructures that are related to orders."""

import uuid
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import AfterValidator, Field

from toolkit.schemas import BaseSchema, TimestampMixin

ORDER_STATUS = Literal["created", "pending", "canceled", "failed"]


def is_decimal_positive(number: Decimal) -> Decimal:
    """Check that the given number is positive or not. If not, raise `ValueError`."""
    if number <= 0:
        raise ValueError("The number be positive")
    return number


class Order(BaseSchema, TimestampMixin):
    """Pydantic schema, modeling an Order in the system."""

    order_id: Annotated[
        uuid.UUID,
        Field(
            description="Unique identifier of the order.",
            default_factory=lambda: uuid.uuid4(),
        ),
    ]
    customer_id: Annotated[int, Field(description="Unique identifier of the customer")]
    items: Annotated[list[str], Field(description="List of items in strings")]
    total_price: Annotated[
        Decimal,
        Field(description="Total price of the order"),
        AfterValidator(is_decimal_positive),
    ]
    status: Annotated[ORDER_STATUS, Field(description="The current state of the order")]

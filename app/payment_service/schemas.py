"""Module defines the schemas and datastructures that are related to payments."""

import uuid
from typing import Annotated, Literal

from pydantic import Field

from toolkit.schemas import BaseSchema, TimestampMixin


class IncomingPayment(BaseSchema):
    """Pydantic schema, modeling an incoming payment in the system."""

    payment_id: Annotated[
        str,
        Field(
            description="The unique identifier of the payment (in string)",
        ),
    ]
    order_id: Annotated[str, Field(description="The unique identifier of the order")]
    status: Annotated[str, Field(description="The state of the payment (in string)")]
    created_at: Annotated[
        str,
        Field(
            description="The datetime (in string) that the payment is created",
            frozen=True,
        ),
    ]


class OutgoingPayment(BaseSchema, TimestampMixin):
    """Pydantic schema, modeling an outgoing payment in the system."""

    payment_id: Annotated[
        uuid.UUID,
        Field(
            description="The unique identifier of the payment",
            default_factory=lambda: uuid.uuid4(),
        ),
    ]
    order_id: Annotated[str, Field(description="The unique identifier of the order")]
    status: Annotated[
        Literal["success", "failed"], Field(description="The state of the payment")
    ]

"""Module defines the schemas and datastructures that are related to payments."""

import uuid
from typing import Annotated, Literal

from pydantic import Field

from toolkit.schemas import BaseSchema, TimestampMixin


class Payment(BaseSchema, TimestampMixin):
    """Pydantic schema, modeling a Payment in the system."""

    payment_id: Annotated[
        uuid.UUID,
        Field(
            description="The unique identifier of the payment",
            default_factory=lambda: uuid.uuid4(),
        ),
    ]
    order_id: Annotated[
        uuid.UUID, Field(description="The unique identifier of the order")
    ]
    status: Annotated[
        Literal["success", "failed"], Field(description="The state of the payment")
    ]

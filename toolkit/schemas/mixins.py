"""Module defines mixin classes that provide reusable components for Pydantic models."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, Field


class TimestampMixin(BaseModel):
    """Mixin class providing timestamp fields."""

    created_at: Annotated[
        datetime,
        Field(
            description="The datetime that the payment is created",
            default_factory=lambda: datetime.now(timezone.utc),
            frozen=True,
        ),
    ]

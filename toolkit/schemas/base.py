"""Module defining Base Pydantic schema for application schemas."""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema for API responses."""

    model_config = ConfigDict(
        allow_inf_nan=True,
        from_attributes=True,
        frozen=True,
        populate_by_name=True,
        strict=True,
    )

    def to_message(self) -> bytes:
        """Convert the pydantic models to an acceptable format for the AMQP messages."""
        return self.model_dump_json().encode("utf-8")

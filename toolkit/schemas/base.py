"""Module defining Base Pydantic schema for application schemas."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """Base schema for API responses."""

    model_config = ConfigDict(
        allow_inf_nan=True,
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        strict=True,
    )

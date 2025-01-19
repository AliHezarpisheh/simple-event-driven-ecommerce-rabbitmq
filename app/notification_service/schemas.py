"""Module defines the schemas and datastructures that are related to notifications."""

from typing import Annotated, Literal

from pydantic import Field

from toolkit.schemas import BaseSchema

NotificationType = Literal["sms", "email", "push"]


class Notification(BaseSchema):
    """Pydantic schema, modeling a notification in the system."""

    type: Annotated[NotificationType, Field(description="The type of the notification")]
    recipient: Annotated[str, Field(description="The email address, phone number, etc")]
    message: Annotated[str, Field(description="The notification message")]

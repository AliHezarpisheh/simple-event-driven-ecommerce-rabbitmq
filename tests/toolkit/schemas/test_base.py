"""Module defines unit tests for `base` schema module."""

import json

import pytest

from toolkit.schemas.base import BaseSchema


class TestSchema(BaseSchema):
    """A subclass of `BaseSchema`, created for testing the parent class methods."""

    __test__ = False

    is_testing: bool


@pytest.fixture(scope="module")
def test_schema() -> TestSchema:
    """Return a `TestSchema` object."""
    return TestSchema(is_testing=True)


def test_to_message_success(test_schema: TestSchema) -> None:
    """Verify the `to_message` functionality."""
    actual_test_schema_dict = json.loads(test_schema.to_message().decode())
    expected_test_schema_dict = test_schema.model_dump()
    assert actual_test_schema_dict == expected_test_schema_dict

"""Module for handling all the settings in the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class for handling all the settings in the application."""

    AMQP_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="forbid"
    )

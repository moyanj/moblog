from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import secrets


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_url: str = Field("", description="Database URL")
    secret_key: str = Field(
        description="Secret key", default_factory=lambda: secrets.token_hex(32)
    )


config = Config()  # type: ignore

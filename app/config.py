import secrets

import dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

dotenv.load_dotenv()


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_url: str = Field("", description="Database URL")
    secret_key: str = Field(description="Secret key", default=secrets.token_hex(32))
    cros_origin: str = Field("*", description="Cross origin")

    host: str = "0.0.0.0"
    port: int = Field(8000, description="Port", le=65535, ge=1)  # 1- 65535


server_config = Config()  # type: ignore

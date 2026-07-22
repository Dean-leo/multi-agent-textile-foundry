"""Environment-backed configuration without secret logging."""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from textile_foundry.exceptions import ConfigurationError


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_base_url: str | None = Field(default=None, validation_alias="OPENAI_BASE_URL")
    openai_model: str | None = Field(default=None, validation_alias="OPENAI_MODEL")
    openai_timeout_seconds: float = Field(
        default=30.0, gt=0, validation_alias="OPENAI_TIMEOUT_SECONDS"
    )
    openai_max_retries: int = Field(default=2, ge=0, le=5, validation_alias="OPENAI_MAX_RETRIES")
    data_dir: Path = Field(default=Path("data"), validation_alias="TEXTILE_DATA_DIR")
    database_url: str = Field(
        default="sqlite+pysqlite:///./textile_foundry.db", validation_alias="DATABASE_URL"
    )

    def require_online_configuration(self) -> None:
        """Validate online-only fields without exposing their values."""
        if self.openai_api_key is None or not self.openai_api_key.get_secret_value():
            raise ConfigurationError("在线模式需要通过 OPENAI_API_KEY 配置模型凭据。")
        if not self.openai_model:
            raise ConfigurationError("在线模式需要通过 OPENAI_MODEL 配置模型名称。")

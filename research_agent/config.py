from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppSettings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
	serpapi_api_key: str = Field(default="", alias="SERPAPI_API_KEY")

	default_model: str = Field(default="gpt-4o-mini")
	request_timeout_seconds: int = Field(default=30)
	user_agent: str = Field(default="research-agent/0.1 (+https://example.local)")


settings = AppSettings()

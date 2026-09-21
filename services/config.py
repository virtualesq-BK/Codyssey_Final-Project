from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All secrets come from environment variables (or a local, git-ignored .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    default_llm_provider: str = "openai"
    default_llm_model: str = ""
    app_env: str = "development"


def get_settings() -> Settings:
    return Settings()

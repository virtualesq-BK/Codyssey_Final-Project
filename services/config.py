from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All secrets come from environment variables (or a local, git-ignored .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    anthropic_base_url: str = ""  # 비우면 공식 API. 코디세이 프록시: https://copa.codyssey.kr
    gemini_api_key: str = ""
    default_llm_provider: str = "openai"
    default_llm_model: str = ""
    app_env: str = "development"


def get_settings() -> Settings:
    return Settings()

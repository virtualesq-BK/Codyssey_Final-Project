from services.config import Settings, get_settings
from services.llm.anthropic_provider import AnthropicProvider
from services.llm.gemini_provider import GeminiProvider
from services.llm.openai_provider import OpenAIProvider
from services.llm.provider import LLMProvider


def create_provider(name: str | None = None, settings: Settings | None = None) -> LLMProvider:
    s = settings or get_settings()
    name = (name or s.default_llm_provider).lower()
    keys = {
        "openai": (OpenAIProvider, s.openai_api_key),
        "anthropic": (AnthropicProvider, s.anthropic_api_key),
        "gemini": (GeminiProvider, s.gemini_api_key),
    }
    if name not in keys:
        raise ValueError(f"Unknown LLM provider: {name}")
    cls, key = keys[name]
    return cls(api_key=key, default_model=s.default_llm_model or None)

from abc import ABC, abstractmethod

from services.llm.usage import LLMUsage, UsageTracker


class LLMProvider(ABC):
    """Agents depend only on this interface, never on a vendor SDK."""

    name: str = "base"

    def __init__(self, api_key: str = "", default_model: str | None = None,
                 tracker: UsageTracker | None = None) -> None:
        self.api_key = api_key
        self.default_model = default_model or None
        self.tracker = tracker or UsageTracker()

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> str: ...

    def record_usage(self, usage: LLMUsage) -> None:
        self.tracker.record(usage)


class FakeLLMProvider(LLMProvider):
    """Deterministic provider for tests; makes no network calls."""

    name = "fake"

    def __init__(self, response: str = "fake response", **kwargs) -> None:
        super().__init__(**kwargs)
        self.response = response

    async def generate(self, system_prompt, user_prompt, model=None, temperature=0.2) -> str:
        self.record_usage(LLMUsage(provider=self.name, model=model or self.default_model))
        return self.response

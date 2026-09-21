from services.llm.provider import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        # TODO: call the Gemini SDK, then self.record_usage(LLMUsage(...)).
        raise NotImplementedError("GeminiProvider is not implemented yet")

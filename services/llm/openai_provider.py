from services.llm.provider import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        # TODO: call the OpenAI SDK, then self.record_usage(LLMUsage(...)).
        raise NotImplementedError("OpenAIProvider is not implemented yet")

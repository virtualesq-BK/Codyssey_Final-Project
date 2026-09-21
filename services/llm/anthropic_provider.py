from services.llm.provider import LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        # TODO: call the Anthropic SDK, then self.record_usage(LLMUsage(...)).
        raise NotImplementedError("AnthropicProvider is not implemented yet")

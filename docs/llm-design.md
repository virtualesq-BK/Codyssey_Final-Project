# LLM Design

- Agent는 `LLMProvider.generate(system_prompt, user_prompt, model, temperature)`에만 의존합니다.
- `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`는 아직 `NotImplementedError`를 발생시키는 skeleton입니다.
- `services/llm/factory.py`의 `create_provider()`가 `DEFAULT_LLM_PROVIDER`/`DEFAULT_LLM_MODEL`을 읽습니다.
- 토큰 사용량은 `LLMUsage`(agent_name, provider, model, input/output/total tokens, latency_ms, estimated_cost, timestamp)와 `UsageTracker`로 기록합니다.
- 테스트에서는 `FakeLLMProvider`를 사용합니다 (네트워크 호출 없음).

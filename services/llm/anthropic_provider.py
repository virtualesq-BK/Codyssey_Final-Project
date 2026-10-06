import time
from typing import Any

import anthropic

from services.llm.provider import LLMProvider
from services.llm.usage import LLMUsage

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_MAX_TOKENS = 16000  # 비스트리밍 요청이 SDK 타임아웃에 걸리지 않는 수준
FALLBACK_BETA = "server-side-fallback-2026-07-01"

# USD per 1M tokens (input, output) — 비용 추정용. 목록에 없는 모델은 추정하지 않는다.
PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-sonnet-4-6": (3.0, 15.0),  # 코디세이 프록시 "claude-sonnet-4"의 실제 응답 모델
}


class LLMRefusalError(RuntimeError):
    """모델(및 fallback 모델)이 안전 정책으로 응답을 거절했을 때."""


class AnthropicProvider(LLMProvider):
    """Claude Messages API 연결.

    - temperature는 보내지 않는다: Opus 5.5 / Sonnet 5.5는 샘플링 파라미터를 400으로 거절한다.
      인터페이스 호환을 위해 인자만 받고 무시한다.
    - 공식 API에서는 거절(refusal) 시 서버 쪽 fallback(`fallbacks="default"`)이 다른 모델로 재시도한다.
      프록시(base_url 지정, 예: 코디세이 copa)는 베타 기능 지원이 보장되지 않아 fallback을 끈다.
    - 최종적으로 거절되면 LLMRefusalError를 던진다 (Agent가 FAILED로 처리).
    """

    name = "anthropic"

    def __init__(
        self,
        api_key: str = "",
        default_model: str | None = None,
        tracker=None,
        effort: str = "medium",
        max_tokens: int = DEFAULT_MAX_TOKENS,
        base_url: str | None = None,
        use_fallbacks: bool | None = None,
        client: Any | None = None,
    ) -> None:
        super().__init__(api_key=api_key, default_model=default_model, tracker=tracker)
        self.effort = effort
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.use_fallbacks = (base_url is None) if use_fallbacks is None else use_fallbacks
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            # api_key가 비어 있으면 SDK가 환경변수 ANTHROPIC_API_KEY 등에서 찾는다
            self._client = anthropic.AsyncAnthropic(
                api_key=self.api_key or None, base_url=self.base_url
            )
        return self._client

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,  # 무시함 — 현재 모델은 샘플링 파라미터 미지원
    ) -> str:
        model_id = model or self.default_model or DEFAULT_MODEL
        started = time.perf_counter()
        request: dict[str, Any] = {
            "model": model_id,
            "max_tokens": self.max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "output_config": {"effort": self.effort},
        }
        if self.use_fallbacks:
            request |= {"betas": [FALLBACK_BETA], "fallbacks": "default"}
        response = await self.client.beta.messages.create(**request)
        latency_ms = (time.perf_counter() - started) * 1000
        self._record(response, model_id, latency_ms)

        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None) if details else None
            raise LLMRefusalError(f"Claude declined the request (category={category})")

        return "".join(block.text for block in response.content if block.type == "text")

    def _record(self, response: Any, requested_model: str, latency_ms: float) -> None:
        usage = response.usage
        served_model = getattr(response, "model", None) or requested_model
        input_tokens, output_tokens = usage.input_tokens, usage.output_tokens
        price = PRICES_PER_MTOK.get(served_model)
        cost = (
            (input_tokens * price[0] + output_tokens * price[1]) / 1_000_000 if price else None
        )
        self.record_usage(
            LLMUsage(
                provider=self.name,
                model=served_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                latency_ms=round(latency_ms, 1),
                estimated_cost=round(cost, 6) if cost is not None else None,
            )
        )

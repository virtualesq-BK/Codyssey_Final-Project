"""AnthropicProvider — 네트워크 없이 가짜 client로 요청 형태·응답 처리·사용량 기록을 검사한다."""

from types import SimpleNamespace

import pytest

from services.llm.anthropic_provider import AnthropicProvider, LLMRefusalError


def _response(stop_reason="end_turn", model="claude-opus-5-5"):
    return SimpleNamespace(
        model=model,
        stop_reason=stop_reason,
        stop_details=SimpleNamespace(category="cyber") if stop_reason == "refusal" else None,
        content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text='{"ok": '),
            SimpleNamespace(type="text", text="true}"),
        ],
        usage=SimpleNamespace(input_tokens=1000, output_tokens=500),
    )


class FakeStream:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get_final_message(self):
        return self._response


class FakeClient:
    def __init__(self, response):
        self.calls: list[dict] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))
        self._response = response

    def _stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeStream(self._response)


async def test_generate_sends_expected_request_and_joins_text():
    client = FakeClient(_response())
    provider = AnthropicProvider(client=client)

    text = await provider.generate("sys", "user", temperature=0.7)

    assert text == '{"ok": true}'  # thinking 블록은 제외, text 블록만 이어붙임
    call = client.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["system"] == "sys"
    assert call["messages"] == [{"role": "user", "content": "user"}]
    assert call["output_config"] == {"effort": "medium"}
    assert call["fallbacks"] == "default"
    assert call["betas"] == ["server-side-fallback-2026-07-01"]
    assert "temperature" not in call  # Opus 5.5는 샘플링 파라미터를 거절함


async def test_default_model_from_settings_is_used():
    client = FakeClient(_response(model="claude-sonnet-5-5"))
    provider = AnthropicProvider(default_model="claude-sonnet-5-5", client=client)
    await provider.generate("s", "u")
    assert client.calls[0]["model"] == "claude-sonnet-5-5"


async def test_usage_is_recorded_with_cost():
    provider = AnthropicProvider(client=FakeClient(_response()))
    await provider.generate("s", "u")

    usage = provider.tracker.records[0]
    assert (usage.input_tokens, usage.output_tokens, usage.total_tokens) == (1000, 500, 1500)
    assert usage.model == "claude-opus-5-5"
    assert usage.estimated_cost == pytest.approx((1000 * 4 + 500 * 20) / 1_000_000)
    assert usage.latency_ms is not None


async def test_refusal_raises():
    provider = AnthropicProvider(client=FakeClient(_response(stop_reason="refusal")))
    with pytest.raises(LLMRefusalError, match="cyber"):
        await provider.generate("s", "u")
    assert len(provider.tracker.records) == 1  # 거절된 호출도 비용은 기록


async def test_proxy_base_url_disables_beta_fallbacks():
    client = FakeClient(_response(model="claude-opus-4-8"))
    provider = AnthropicProvider(base_url="https://copa.codyssey.kr", client=client)
    await provider.generate("s", "u", model="claude-opus-4-8")
    call = client.calls[0]
    assert "fallbacks" not in call and "betas" not in call
    assert call["model"] == "claude-opus-4-8"

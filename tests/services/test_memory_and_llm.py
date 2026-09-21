import pytest

from services.config import Settings
from services.llm.factory import create_provider
from services.llm.openai_provider import OpenAIProvider
from services.llm.provider import FakeLLMProvider
from services.memory.memory_service import MemoryService
from services.memory.schemas import MemoryRecord


async def test_memory_roundtrip_by_user():
    svc = MemoryService()
    await svc.save(MemoryRecord(user_id="u1", feedback=["good"]))
    await svc.save(MemoryRecord(user_id="u2"))
    history = await svc.get_user_history("u1")
    assert len(history) == 1 and history[0].feedback == ["good"]


def test_factory_uses_settings_default():
    provider = create_provider(settings=Settings(default_llm_provider="openai", _env_file=None))
    assert isinstance(provider, OpenAIProvider)


def test_factory_rejects_unknown_provider():
    with pytest.raises(ValueError):
        create_provider("nope", settings=Settings(_env_file=None))


async def test_fake_provider_records_usage():
    p = FakeLLMProvider(response="hi")
    assert await p.generate("s", "u") == "hi"
    assert p.tracker.records[0].provider == "fake"

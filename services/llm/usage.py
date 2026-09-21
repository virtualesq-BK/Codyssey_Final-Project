from datetime import UTC, datetime

from pydantic import BaseModel, Field


class LLMUsage(BaseModel):
    agent_name: str | None = None
    provider: str
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: float | None = None
    estimated_cost: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UsageTracker:
    """In-memory sink; swap for a DB-backed implementation later."""

    def __init__(self) -> None:
        self.records: list[LLMUsage] = []

    def record(self, usage: LLMUsage) -> None:
        self.records.append(usage)

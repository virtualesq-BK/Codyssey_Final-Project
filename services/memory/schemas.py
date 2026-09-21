from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    user_id: str
    business_idea_id: str | None = None
    analysis_id: str | None = None
    decision_history: list[dict[str, Any]] = Field(default_factory=list)
    feedback: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

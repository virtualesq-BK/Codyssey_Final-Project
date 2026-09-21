from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_IMPLEMENTED = "not_implemented"


class Evidence(BaseModel):
    source_title: str
    source_type: str
    url: str | None = None
    claim: str
    published_at: date | None = None
    relevance: float = Field(default=0.0, ge=0.0, le=1.0)


class AgentResult(BaseModel):
    agent_name: str
    status: AgentStatus
    summary: str = ""
    findings: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

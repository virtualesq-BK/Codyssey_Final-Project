from datetime import date, datetime
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
    # Legal & Compliance Agent 전용 필드 (선택, 다른 Agent는 사용하지 않아도 됨)
    source_level: str | None = None   # e.g. "statute", "regulation", "guideline"
    citation: str | None = None       # e.g. "공정거래법 제3조 제1항"
    retrieved_at: datetime | None = None  # 법령 조회 시각


class AgentResult(BaseModel):
    agent_name: str
    status: AgentStatus
    summary: str = ""
    findings: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

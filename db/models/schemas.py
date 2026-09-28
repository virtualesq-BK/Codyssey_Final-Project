"""
DB 모델 스키마 (ORM 독립적인 Pydantic 계약).

D 담당자가 이 인터페이스를 기반으로 SQLAlchemy/SQLModel 모델을 구현합니다.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class BusinessIdeaRecord(BaseModel):
    id: str
    user_id: str | None = None
    title: str
    description: str = ""
    target_customer: str = ""
    industry: str = ""
    geography: str = ""
    country: str = ""
    business_model: str = ""
    price: float | None = None
    additional_context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AnalysisRecord(BaseModel):
    id: str
    business_idea_id: str
    status: str = "processing"  # "processing" | "completed" | "failed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None


class AgentResultRecord(BaseModel):
    id: str
    analysis_id: str
    agent_name: str
    status: str
    summary: str = ""
    findings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceRecord(BaseModel):
    id: str
    agent_result_id: str
    source_title: str
    source_type: str
    url: str | None = None
    claim: str
    relevance: float = 0.0
    source_level: str | None = None
    citation: str | None = None


class DecisionResultRecord(BaseModel):
    id: str
    analysis_id: str
    executive_summary: str = ""
    market_assessment: str = ""
    customer_assessment: str = ""
    competition_assessment: str = ""
    business_model_assessment: str = ""
    financial_assessment: str = ""
    risk_assessment: str = ""
    legal_compliance_assessment: str = ""
    key_findings: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    action_plan: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class FeedbackRecord(BaseModel):
    id: str
    analysis_id: str
    user_id: str | None = None
    rating: int | None = None  # 1-5
    comment: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

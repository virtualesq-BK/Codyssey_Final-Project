from pydantic import BaseModel, Field

from domain.agent_result import Evidence


class DecisionResult(BaseModel):
    executive_summary: str = ""
    market_assessment: str = ""
    customer_assessment: str = ""
    competition_assessment: str = ""
    business_model_assessment: str = ""
    financial_assessment: str = ""
    risk_assessment: str = ""
    key_findings: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    action_plan: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)

"""Customer Agent 출력 스키마 (docs/agents/customer-bm.md 4-1).

LLM 응답은 CustomerLLMOutput으로 검증하고, 그중 분석 본문을 AgentResult.metadata에 담는다.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Grade = Literal["A", "B", "C", "D"]

SCHEMA_VERSION = "c-0.2"


class GradedText(BaseModel):
    text: str
    grade: Grade = "D"


class ProblemStatement(BaseModel):
    text: str
    frequency: str = ""
    grade: Grade = "D"


class JTBD(BaseModel):
    when: str
    want: str
    so_that: str
    functional: str = ""
    emotional: str = ""
    social: str = ""


class Alternative(BaseModel):
    method: str
    cost_or_pain: str = ""
    pain_score: int = Field(default=3, ge=1, le=5)
    grade: Grade = "D"


class Segment(BaseModel):
    id: str  # "S1", "S2" … — 다른 칸은 이 id로 가리킨다
    name: str
    size: int = Field(ge=1, le=5)
    pain: int = Field(ge=1, le=5)
    willingness_to_pay: int = Field(ge=1, le=5)
    reach: int = Field(ge=1, le=5)
    total: int = 0  # 코드가 다시 계산한다
    grade: Grade = "D"


class Beachhead(BaseModel):
    segment_id: str  # segments[].id
    reason: str = ""


class UserVsPayer(BaseModel):
    user: str
    payer: str
    same: bool


class Persona(BaseModel):
    name: str
    profile: str
    day: str = ""
    worst_moment: str = ""
    tools: list[str] = Field(default_factory=list)
    buying_power: str = ""
    is_hypothetical: bool = True


class Hypothesis(BaseModel):
    id: str
    statement: str
    grade: Grade = "D"
    validation: str = ""


class CustomerAnalysis(BaseModel):
    """metadata에 저장되는 분석 본문."""

    problem_statement: ProblemStatement
    jtbd: JTBD
    alternatives: list[Alternative] = Field(min_length=2)
    segments: list[Segment] = Field(min_length=1)
    beachhead: Beachhead
    user_vs_payer: UserVsPayer
    personas: list[Persona] = Field(min_length=1, max_length=2)
    purchase_drivers: list[str] = Field(default_factory=list)
    purchase_barriers: list[str] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_segment_refs(self) -> "CustomerAnalysis":
        ids = [s.id for s in self.segments]
        if len(ids) != len(set(ids)):
            raise ValueError("segments[].id must be unique")
        if self.beachhead.segment_id not in ids:
            raise ValueError("beachhead.segment_id must match one of segments[].id")
        return self


class CustomerLLMOutput(CustomerAnalysis):
    """LLM이 돌려줘야 하는 전체 JSON = 분석 본문 + 요약용 칸."""

    summary: str
    key_findings: list[GradedText] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

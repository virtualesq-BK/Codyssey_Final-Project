"""Business Model Agent 출력 스키마 (docs/agents/customer-bm.md 4-2)."""

from typing import Literal

from pydantic import BaseModel, Field

Grade = Literal["A", "B", "C", "D"]
BillingPeriod = Literal["month", "year", "one_time", "per_use"]
PayerType = Literal["B2C", "B2B", "B2G"]

SCHEMA_VERSION = "c-0.2"


class GradedText(BaseModel):
    text: str
    grade: Grade = "D"


class ValueProposition(BaseModel):
    for_whom: str
    problem: str
    offer: str
    unlike: str = ""


class RevenueModelCandidate(BaseModel):
    model: str
    fit: float = Field(ge=0.0, le=1.0)
    rationale: str = ""
    grade: Grade = "D"


class Pricing(BaseModel):
    price_krw: int = Field(ge=0)
    billing_period: BillingPeriod
    unit: str  # 무엇 1개당 가격인가: user / school / center / seat / case ...
    range_low_krw: int = Field(ge=0)
    range_high_krw: int = Field(ge=0)
    rationale: str = ""
    grade: Grade = "D"


class PriceTier(BaseModel):
    plan: str
    price_krw: int = Field(ge=0)
    includes: str = ""
    target: str = ""


class FreeVsPaid(BaseModel):
    free: list[str] = Field(default_factory=list)
    paid: list[str] = Field(default_factory=list)


class Channel(BaseModel):
    channel: str
    role: str = ""  # 인지 | 구매 | 전달
    grade: Grade = "D"


class Acquisition(BaseModel):
    tactic: str
    target_segment: str = ""
    grade: Grade = "D"


class HandoffToFinancial(BaseModel):
    """D(Financial)에게 넘기는 값. 코드가 pricing + payer_type으로 만든다."""

    price_krw: int
    billing_period: BillingPeriod
    unit: str
    payer_type: PayerType
    # D 계산기는 월 기준 (FinancialInputs.avg_revenue_per_customer_month).
    # 연 가격은 12로 나눈 값, 1회·건당 가격은 반복 매출이 아니므로 None.
    monthly_equivalent_krw: int | None


class BusinessModelAnalysis(BaseModel):
    """metadata에 저장되는 분석 본문."""

    value_proposition: ValueProposition
    revenue_model_candidates: list[RevenueModelCandidate] = Field(min_length=2, max_length=4)
    chosen_model: str
    payer_type: PayerType
    pricing: Pricing
    price_ladder: list[PriceTier] = Field(default_factory=list)
    free_vs_paid: FreeVsPaid = Field(default_factory=FreeVsPaid)
    channels: list[Channel] = Field(min_length=1)
    acquisition: list[Acquisition] = Field(default_factory=list)
    key_resources: list[str] = Field(default_factory=list)
    key_activities: list[str] = Field(default_factory=list)
    key_partners: list[str] = Field(default_factory=list)
    cost_drivers: list[str] = Field(default_factory=list)


class BusinessModelLLMOutput(BusinessModelAnalysis):
    """LLM이 돌려줘야 하는 전체 JSON = 분석 본문 + 요약용 칸."""

    summary: str
    key_findings: list[GradedText] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

"""Business Model Agent — "누구에게, 어떤 방식으로, 얼마를 받아 돈을 버나?"

기획서 원안의 2단계 에이전트. 1단계 결과(특히 고객 분석)가
BusinessIdea.additional_context["customer_analysis"]로 들어오면 그 결론을 바탕으로 설계하고,
없으면 아이디어만 보고 혼자 분석한다.

흐름: (RAG 검색) → 프롬프트 → LLM → JSON 추출 → 스키마 검증 → 코드 후처리 → AgentResult
설계: docs/agents/customer-bm.md
"""

from pydantic import ValidationError

from agents.base.agent import BaseAgent
from agents.business_model.parsing import extract_json_object
from agents.business_model.prompts import build_system_prompt, build_user_prompt, upstream_context
from agents.business_model.schemas import (
    SCHEMA_VERSION,
    BusinessModelAnalysis,
    BusinessModelLLMOutput,
    HandoffToFinancial,
)
from domain.agent_result import AgentResult, AgentStatus, Evidence
from domain.business_idea import BusinessIdea
from services.llm.provider import LLMProvider
from services.rag.rag_service import RAGService
from services.rag.schemas import SearchResult

GRADE_WEIGHT = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25}
MAX_FINDINGS = 5
MAX_RECOMMENDATIONS = 3
RAG_TOP_K = 5


class BusinessModelAgent(BaseAgent):
    name = "business_model"

    def __init__(self, llm: LLMProvider | None = None, rag: RAGService | None = None) -> None:
        self.llm = llm
        self.rag = rag

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        if self.llm is None:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                summary="LLM provider가 설정되지 않아 비즈니스 모델 분석을 실행하지 못했습니다.",
                metadata={"error_type": "MissingLLMProvider", "schema_version": SCHEMA_VERSION},
            )
        try:
            references = await self._search(input_data)
            raw = await self.llm.generate(
                build_system_prompt(), build_user_prompt(input_data, references)
            )
        except Exception as exc:  # noqa: BLE001 — 한 Agent 실패가 전체를 멈추지 않게
            return self.failed_result(exc)

        evidence = [_to_evidence(r) for r in references]
        data = extract_json_object(raw)
        if data is None:
            return self._partial("LLM 응답에서 JSON을 찾지 못했습니다.", evidence, raw)
        try:
            output = BusinessModelLLMOutput.model_validate(data)
        except ValidationError as exc:
            errors = [".".join(map(str, e["loc"])) for e in exc.errors()]
            return self._partial(
                f"LLM 응답이 형식에 맞지 않습니다 ({len(errors)}개 오류).", evidence, raw, errors
            )
        return self._build_result(output, input_data, evidence)

    async def _search(self, idea: BusinessIdea) -> list[SearchResult]:
        if self.rag is None:
            return []
        query = " ".join(filter(None, [idea.title, idea.industry, "가격 수익모델 요금제"]))
        return await self.rag.search(query, top_k=RAG_TOP_K)

    def _build_result(
        self, output: BusinessModelLLMOutput, idea: BusinessIdea, evidence: list[Evidence]
    ) -> AgentResult:
        analysis = BusinessModelAnalysis.model_validate(output.model_dump())
        pricing = analysis.pricing
        handoff = HandoffToFinancial(
            price_krw=pricing.price_krw,
            billing_period=pricing.billing_period,
            unit=pricing.unit,
            payer_type=analysis.payer_type,
            monthly_equivalent_krw=_monthly_equivalent(pricing.price_krw, pricing.billing_period),
        )
        upstream = upstream_context(idea)

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            summary=output.summary,
            findings=[f"{f.text} [{f.grade}]" for f in output.key_findings[:MAX_FINDINGS]],
            evidence=evidence,
            recommendations=output.recommendations[:MAX_RECOMMENDATIONS],
            confidence=_confidence(analysis, output),
            metadata={
                "schema_version": SCHEMA_VERSION,
                **analysis.model_dump(),
                "handoff_to_financial": handoff.model_dump(),
                "used_upstream": sorted(upstream),
                "quality_checks": _quality_checks(analysis),
            },
        )

    def _partial(
        self, reason: str, evidence: list[Evidence], raw: str, errors: list[str] | None = None
    ) -> AgentResult:
        metadata: dict = {"schema_version": SCHEMA_VERSION, "raw_response": raw[:2000]}
        if errors:
            metadata["validation_errors"] = errors
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.PARTIAL,
            summary=f"INSUFFICIENT_EVIDENCE — {reason}",
            evidence=evidence,
            confidence=0.0,
            metadata=metadata,
        )


def _monthly_equivalent(price_krw: int, billing_period: str) -> int | None:
    if billing_period == "month":
        return price_krw
    if billing_period == "year":
        return round(price_krw / 12)
    return None


def _to_evidence(result: SearchResult) -> Evidence:
    doc = result.document
    return Evidence(
        source_title=doc.title,
        source_type=doc.source_type,
        url=doc.url,
        claim=doc.content[:300],
        published_at=doc.published_at,
        relevance=max(0.0, min(1.0, result.score)),
    )


def _confidence(analysis: BusinessModelAnalysis, output: BusinessModelLLMOutput) -> float:
    """핵심 주장들의 근거 등급 평균 (A=1.0 … D=0.25)."""
    grades = [analysis.pricing.grade]
    grades += [c.grade for c in analysis.revenue_model_candidates]
    grades += [c.grade for c in analysis.channels]
    grades += [f.grade for f in output.key_findings[:MAX_FINDINGS]]
    return round(sum(GRADE_WEIGHT[g] for g in grades) / len(grades), 2)


def _quality_checks(analysis: BusinessModelAnalysis) -> dict[str, bool]:
    """설계서 5장 중 코드로 검사할 수 있는 항목."""
    p = analysis.pricing
    names = [c.model for c in analysis.revenue_model_candidates]
    best = max(analysis.revenue_model_candidates, key=lambda c: c.fit)
    return {
        "chosen_model_in_candidates": analysis.chosen_model in names,
        "chosen_model_is_best_fit": analysis.chosen_model == best.model,
        "price_within_range": p.range_low_krw <= p.price_krw <= p.range_high_krw,
        "price_has_rationale": bool(p.rationale.strip()),
        "price_ladder_within_range": all(
            p.range_low_krw <= t.price_krw <= p.range_high_krw for t in analysis.price_ladder
        ),
    }

"""Customer Agent — "누가, 어떤 상황에서, 얼마나 아파하나?"

흐름: (RAG 검색) → 프롬프트 → LLM → JSON 추출 → 스키마 검증 → 코드 후처리 → AgentResult
설계: docs/agents/customer-bm.md
"""

from pydantic import ValidationError

from agents.base.agent import BaseAgent
from agents.customer.parsing import extract_json_object
from agents.customer.prompts import build_system_prompt, build_user_prompt
from agents.customer.schemas import SCHEMA_VERSION, CustomerAnalysis, CustomerLLMOutput
from domain.agent_result import AgentResult, AgentStatus, Evidence
from domain.business_idea import BusinessIdea
from services.llm.provider import LLMProvider
from services.rag.rag_service import RAGService
from services.rag.schemas import SearchResult

GRADE_WEIGHT = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25}
MAX_FINDINGS = 5
MAX_RECOMMENDATIONS = 3
RAG_TOP_K = 5


class CustomerAgent(BaseAgent):
    name = "customer"

    def __init__(self, llm: LLMProvider | None = None, rag: RAGService | None = None) -> None:
        self.llm = llm
        self.rag = rag

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        if self.llm is None:
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                summary="LLM provider가 설정되지 않아 고객 분석을 실행하지 못했습니다.",
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
            output = CustomerLLMOutput.model_validate(data)
        except ValidationError as exc:
            errors = [".".join(map(str, e["loc"])) for e in exc.errors()]
            return self._partial(
                f"LLM 응답이 형식에 맞지 않습니다 ({len(errors)}개 오류).", evidence, raw, errors
            )
        return self._build_result(output, input_data, evidence)

    async def _search(self, idea: BusinessIdea) -> list[SearchResult]:
        if self.rag is None:
            return []
        query = " ".join(filter(None, [idea.title, idea.target_customer, idea.industry, "고객"]))
        return await self.rag.search(query, top_k=RAG_TOP_K)

    def _build_result(
        self, output: CustomerLLMOutput, idea: BusinessIdea, evidence: list[Evidence]
    ) -> AgentResult:
        analysis = CustomerAnalysis.model_validate(output.model_dump())

        # 계산 가능한 값은 LLM이 아니라 코드가 정한다
        for seg in analysis.segments:
            seg.total = seg.size + seg.pain + seg.willingness_to_pay + seg.reach
        if not idea.additional_context:  # 인터뷰 자료가 없으면 페르소나는 무조건 가상
            for persona in analysis.personas:
                persona.is_hypothetical = True

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


def _confidence(analysis: CustomerAnalysis, output: CustomerLLMOutput) -> float:
    """핵심 주장들의 근거 등급 평균 (A=1.0 … D=0.25)."""
    grades = [analysis.problem_statement.grade]
    grades += [a.grade for a in analysis.alternatives]
    grades += [s.grade for s in analysis.segments]
    grades += [f.grade for f in output.key_findings[:MAX_FINDINGS]]
    return round(sum(GRADE_WEIGHT[g] for g in grades) / len(grades), 2)


def _quality_checks(analysis: CustomerAnalysis) -> dict[str, bool]:
    """설계서 5장 중 코드로 검사할 수 있는 항목."""
    top = max(analysis.segments, key=lambda s: s.total)
    return {
        "has_user_vs_payer": bool(analysis.user_vs_payer.user and analysis.user_vs_payer.payer),
        "has_do_nothing_alternative": any(
            "아무것도" in a.method or "안 함" in a.method for a in analysis.alternatives
        ),
        "beachhead_is_top_segment": analysis.beachhead.segment_id == top.id,
        "beachhead_has_reason": bool(analysis.beachhead.reason.strip()),
        "has_hypotheses": len(analysis.hypotheses) > 0,
    }

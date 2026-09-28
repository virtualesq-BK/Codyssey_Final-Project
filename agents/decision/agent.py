"""
Decision Agent

역할:
    전문 Agent의 구조화된 AgentResult 를 종합해 DecisionResult 를 생성합니다.
    자체적으로 새로운 시장조사·법률조사를 수행하지 않습니다.
    RAG 원문 전체를 받지 않고, 각 Agent가 요약한 Evidence 만 받습니다.
    근거가 부족하면 "INSUFFICIENT_EVIDENCE" 또는 "추가 검증 필요" 로 표시합니다.

TODO (A 담당자):
    LLM 종합 로직을 구현합니다.
    각 assessment 필드를 해당 Agent 결과로 채웁니다.
"""

from agents.base.agent import BaseAgent
from domain.agent_result import AgentResult, AgentStatus
from domain.business_idea import BusinessIdea
from domain.decision_result import DecisionResult
from services.llm.provider import LLMProvider

_INSUFFICIENT = "INSUFFICIENT_EVIDENCE"


class DecisionAgent(BaseAgent):
    """구조화된 AgentResult 목록만 입력받아 DecisionResult 를 생성합니다."""

    name = "decision"

    def __init__(self, llm: LLMProvider | None = None) -> None:
        self.llm = llm

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        return self.not_implemented_result()

    async def decide(self, idea: BusinessIdea, results: list[AgentResult]) -> DecisionResult:
        """
        각 전문 Agent 결과를 DecisionResult 의 각 필드에 매핑합니다.

        skeleton 구현:
            - agent_name 으로 어느 필드에 들어갈지 결정
            - 근거(evidence)가 없으면 INSUFFICIENT_EVIDENCE
            - TODO: LLM 으로 summary 합성
        """
        by_agent: dict[str, AgentResult] = {r.agent_name: r for r in results}

        def _assess(agent_name: str) -> str:
            r = by_agent.get(agent_name)
            if r is None:
                return _INSUFFICIENT
            if r.status == AgentStatus.FAILED:
                return f"분석 실패: {r.summary}"
            if r.status == AgentStatus.NOT_IMPLEMENTED:
                return "추가 검증 필요"
            if not r.evidence:
                return _INSUFFICIENT
            return r.summary or _INSUFFICIENT

        confs = [r.confidence for r in results]
        return DecisionResult(
            executive_summary=(
                # TODO: LLM 종합 문장 생성
                f"'{idea.title}' 사업 아이디어 종합 분석 결과 (skeleton)"
            ),
            market_assessment=_assess("market"),
            customer_assessment=_assess("customer"),
            competition_assessment=_assess("competitor"),
            business_model_assessment=_assess("business_model"),
            financial_assessment=_assess("financial"),
            risk_assessment=_assess("risk"),
            legal_compliance_assessment=_assess("legal_compliance"),
            key_findings=[f for r in results for f in r.findings],
            evidence=[e for r in results for e in r.evidence],
            confidence=sum(confs) / len(confs) if confs else 0.0,
        )

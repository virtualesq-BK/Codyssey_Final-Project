"""
Orchestrator Agent

역할:
    1. BusinessIdea 기본 검증
    2. 필요한 전문 Agent 결정 (주입받은 목록 사용)
    3. 전문 Agent 병렬 실행
    4. 실패 Agent → FAILED AgentResult 로 대체 (워크플로 중단 방지)
    5. 수집된 AgentResult → Decision Agent 전달
    6. DecisionResult 반환

전문 Agent 목록 (기본값):
    Market / Competitor / Customer / BusinessModel
    Financial / Risk / LegalCompliance

Decision Agent에는 raw RAG 문서를 전달하지 않습니다.
각 Agent의 구조화된 AgentResult 와 evidence 만 전달합니다.
"""

import asyncio
from agents.base.agent import BaseAgent
from agents.decision.agent import DecisionAgent
from domain.agent_result import AgentResult, AgentStatus
from domain.business_idea import BusinessIdea
from domain.decision_result import DecisionResult


class OrchestratorAgent(BaseAgent):
    """
    주입받은 전문 Agent를 병렬 실행하고 DecisionAgent에 결과를 넘깁니다.

    사용 예::

        agents = [MarketAgent(), CompetitorAgent(), ..., LegalComplianceAgent()]
        orch   = OrchestratorAgent(agents=agents)
        results, decision = await orch.analyze(idea)
    """

    name = "orchestrator"

    def __init__(
        self,
        agents: list[BaseAgent] | None = None,
        decision: DecisionAgent | None = None,
    ) -> None:
        self.agents = agents or []
        self.decision = decision or DecisionAgent()

    # ------------------------------------------------------------------ #
    # BaseAgent interface                                                  #
    # ------------------------------------------------------------------ #

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        """단일 AgentResult 계약을 만족하기 위한 진입점 (내부적으로 analyze 사용 권장)."""
        return self.not_implemented_result()

    # ------------------------------------------------------------------ #
    # Main workflow                                                        #
    # ------------------------------------------------------------------ #

    async def analyze(
        self, idea: BusinessIdea
    ) -> tuple[list[AgentResult], DecisionResult]:
        """
        전체 분석 워크플로를 실행합니다.

        1. BusinessIdea 검증
        2. 전문 Agent 병렬 실행
        3. Decision Agent 종합
        """
        validation_error = self._validate_idea(idea)
        if validation_error:
            failed: AgentResult = AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                summary=validation_error,
                confidence=0.0,
            )
            return [failed], DecisionResult(executive_summary=validation_error)

        results = list(
            await asyncio.gather(*(self._run_one(a, idea) for a in self.agents))
        )
        decision = await self.decision.decide(idea, results)
        return results, decision

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    async def _run_one(self, agent: BaseAgent, idea: BusinessIdea) -> AgentResult:
        """한 Agent 실패가 전체 워크플로를 중단하지 않도록 감쌉니다."""
        try:
            return await agent.run(idea)
        except Exception as exc:  # noqa: BLE001
            return agent.failed_result(exc)

    @staticmethod
    def _validate_idea(idea: BusinessIdea) -> str | None:
        """필수 필드 검증. 문제가 없으면 None 반환."""
        if not idea.title.strip():
            return "BusinessIdea.title은 비어 있을 수 없습니다."
        return None

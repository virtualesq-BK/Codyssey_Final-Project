"""멀티 Agent 워크플로 통합 테스트."""

from agents.base.agent import BaseAgent
from agents.business_model import BusinessModelAgent
from agents.competitor import CompetitorAgent
from agents.customer import CustomerAgent
from agents.financial import FinancialAgent
from agents.legal_compliance import LegalComplianceAgent
from agents.market import MarketAgent
from agents.orchestrator import OrchestratorAgent
from agents.risk import RiskAgent
from domain.agent_result import AgentStatus
from domain.decision_result import DecisionResult


class BoomAgent(BaseAgent):
    name = "boom"

    async def run(self, input_data):
        raise RuntimeError("boom")


ALL_AGENTS = [
    MarketAgent(),
    CompetitorAgent(),
    CustomerAgent(),
    BusinessModelAgent(),
    FinancialAgent(),
    RiskAgent(),
    LegalComplianceAgent(),
]


async def test_multi_agent_workflow_all_7(idea):
    results, decision = await OrchestratorAgent(ALL_AGENTS).analyze(idea)
    assert len(results) == 7
    assert isinstance(decision, DecisionResult)
    assert 0.0 <= decision.confidence <= 1.0
    # DecisionResult에 legal_compliance_assessment 가 있어야 함
    assert hasattr(decision, "legal_compliance_assessment")


async def test_workflow_survives_failing_agent(idea):
    results, decision = await OrchestratorAgent([MarketAgent(), BoomAgent()]).analyze(idea)
    statuses = {r.agent_name: r.status for r in results}
    assert statuses["boom"] == AgentStatus.FAILED
    assert isinstance(decision, DecisionResult)


async def test_orchestrator_validates_empty_title():
    from domain.business_idea import BusinessIdea

    empty_idea = BusinessIdea(title=" ")
    # _validate_idea 가 공백 title 을 잡아야 함
    results, decision = await OrchestratorAgent(ALL_AGENTS).analyze(empty_idea)
    assert results[0].status == AgentStatus.FAILED
    assert "title" in results[0].summary.lower() or "비어" in results[0].summary

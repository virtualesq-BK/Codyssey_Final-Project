from agents.base.agent import BaseAgent
from agents.business_model import BusinessModelAgent
from agents.competitor import CompetitorAgent
from agents.customer import CustomerAgent
from agents.financial import FinancialAgent
from agents.market import MarketAgent
from agents.orchestrator import OrchestratorAgent
from agents.risk import RiskAgent
from domain.agent_result import AgentStatus
from domain.decision_result import DecisionResult


class BoomAgent(BaseAgent):
    name = "boom"

    async def run(self, input_data):
        raise RuntimeError("boom")


async def test_multi_agent_workflow(idea):
    agents = [MarketAgent(), CompetitorAgent(), CustomerAgent(), BusinessModelAgent(),
              FinancialAgent(), RiskAgent()]
    results, decision = await OrchestratorAgent(agents).analyze(idea)
    assert len(results) == 6
    assert isinstance(decision, DecisionResult)
    assert 0.0 <= decision.confidence <= 1.0


async def test_workflow_survives_failing_agent(idea):
    results, decision = await OrchestratorAgent([MarketAgent(), BoomAgent()]).analyze(idea)
    assert results[1].status == AgentStatus.FAILED
    assert isinstance(decision, DecisionResult)

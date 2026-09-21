
from agents.risk import RiskAgent
from domain.agent_result import AgentResult, AgentStatus
from services.llm.provider import FakeLLMProvider


async def test_risk_agent_contract(idea):
    agent = RiskAgent(llm=FakeLLMProvider())
    result = await agent.run(idea)
    assert isinstance(result, AgentResult)
    assert result.agent_name == "risk"
    assert result.status in set(AgentStatus)
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.evidence, list)


async def test_risk_agent_runs_without_dependencies(idea):
    result = await RiskAgent().run(idea)
    AgentResult.model_validate(result.model_dump())


from agents.orchestrator import OrchestratorAgent
from domain.agent_result import AgentResult, AgentStatus


async def test_orchestrator_agent_contract(idea):
    agent = OrchestratorAgent()
    result = await agent.run(idea)
    assert isinstance(result, AgentResult)
    assert result.agent_name == "orchestrator"
    assert result.status in set(AgentStatus)
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.evidence, list)


async def test_orchestrator_agent_runs_without_dependencies(idea):
    result = await OrchestratorAgent().run(idea)
    AgentResult.model_validate(result.model_dump())

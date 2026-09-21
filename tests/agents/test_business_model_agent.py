
from agents.business_model import BusinessModelAgent
from domain.agent_result import AgentResult, AgentStatus
from services.llm.provider import FakeLLMProvider


async def test_business_model_agent_contract(idea):
    agent = BusinessModelAgent(llm=FakeLLMProvider())
    result = await agent.run(idea)
    assert isinstance(result, AgentResult)
    assert result.agent_name == "business_model"
    assert result.status in set(AgentStatus)
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.evidence, list)


async def test_business_model_agent_runs_without_dependencies(idea):
    result = await BusinessModelAgent().run(idea)
    AgentResult.model_validate(result.model_dump())

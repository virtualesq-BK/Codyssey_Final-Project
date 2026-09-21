
from agents.customer import CustomerAgent
from domain.agent_result import AgentResult, AgentStatus
from services.llm.provider import FakeLLMProvider


async def test_customer_agent_contract(idea):
    agent = CustomerAgent(llm=FakeLLMProvider())
    result = await agent.run(idea)
    assert isinstance(result, AgentResult)
    assert result.agent_name == "customer"
    assert result.status in set(AgentStatus)
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.evidence, list)


async def test_customer_agent_runs_without_dependencies(idea):
    result = await CustomerAgent().run(idea)
    AgentResult.model_validate(result.model_dump())

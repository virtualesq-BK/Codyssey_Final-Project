import asyncio

from agents.base.agent import BaseAgent
from agents.decision.agent import DecisionAgent
from domain.agent_result import AgentResult
from domain.business_idea import BusinessIdea
from domain.decision_result import DecisionResult


class OrchestratorAgent(BaseAgent):
    """Runs injected specialist agents in parallel, then hands results to Decision."""

    name = "orchestrator"

    def __init__(
        self, agents: list[BaseAgent] | None = None, decision: DecisionAgent | None = None
    ) -> None:
        self.agents = agents or []
        self.decision = decision or DecisionAgent()

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        return self.not_implemented_result()

    async def _run_one(self, agent: BaseAgent, idea: BusinessIdea) -> AgentResult:
        try:
            return await agent.run(idea)
        except Exception as exc:  # one failing agent must not sink the workflow
            return agent.failed_result(exc)

    async def analyze(self, idea: BusinessIdea) -> tuple[list[AgentResult], DecisionResult]:
        results = list(await asyncio.gather(*(self._run_one(a, idea) for a in self.agents)))
        return results, await self.decision.decide(idea, results)

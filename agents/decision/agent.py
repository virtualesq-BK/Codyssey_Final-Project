from agents.base.agent import BaseAgent
from domain.agent_result import AgentResult
from domain.business_idea import BusinessIdea
from domain.decision_result import DecisionResult
from services.llm.provider import LLMProvider


class DecisionAgent(BaseAgent):
    """Consumes structured AgentResults only, never raw RAG documents."""

    name = "decision"

    def __init__(self, llm: LLMProvider | None = None) -> None:
        self.llm = llm

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        return self.not_implemented_result()

    async def decide(self, idea: BusinessIdea, results: list[AgentResult]) -> DecisionResult:
        # TODO: LLM synthesis. Skeleton aggregates deterministically.
        confs = [r.confidence for r in results]
        return DecisionResult(
            executive_summary=f"Skeleton decision for '{idea.title}'.",
            key_findings=[f for r in results for f in r.findings],
            confidence=sum(confs) / len(confs) if confs else 0.0,
            evidence=[e for r in results for e in r.evidence],
        )

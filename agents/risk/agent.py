from agents.base.agent import BaseAgent
from domain.agent_result import AgentResult
from domain.business_idea import BusinessIdea
from services.llm.provider import LLMProvider
from services.rag.rag_service import RAGService


class RiskAgent(BaseAgent):
    name = "risk"

    def __init__(self, llm: LLMProvider | None = None, rag: RAGService | None = None) -> None:
        self.llm = llm
        self.rag = rag

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        # TODO: rag.search -> Evidence -> Finding -> Recommendation
        return self.not_implemented_result()

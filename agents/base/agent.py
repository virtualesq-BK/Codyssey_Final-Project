from domain.agent_result import AgentResult, AgentStatus
from domain.business_idea import BusinessIdea


class BaseAgent:
    """Common interface. Agents exchange data only through AgentResult."""

    name: str = "base"

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        raise NotImplementedError

    def not_implemented_result(self) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.NOT_IMPLEMENTED,
            summary=f"{self.name} is a skeleton; logic not implemented yet.",
            confidence=0.0,
        )

    def failed_result(self, error: Exception) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.FAILED,
            summary=str(error),
            confidence=0.0,
            metadata={"error_type": type(error).__name__},
        )

"""
Repository Contract (Abstract Base Classes).

D 담당자가 이 계약을 구현합니다.
다른 레이어는 이 인터페이스에만 의존하고 구체 구현에 의존하지 않습니다.
"""

from abc import ABC, abstractmethod

from db.models.schemas import (
    AgentResultRecord,
    AnalysisRecord,
    BusinessIdeaRecord,
    DecisionResultRecord,
    EvidenceRecord,
    FeedbackRecord,
)


class BusinessIdeaRepository(ABC):
    @abstractmethod
    async def save(self, record: BusinessIdeaRecord) -> None: ...

    @abstractmethod
    async def get(self, id: str) -> BusinessIdeaRecord | None: ...

    @abstractmethod
    async def list_by_user(self, user_id: str) -> list[BusinessIdeaRecord]: ...


class AnalysisRepository(ABC):
    @abstractmethod
    async def save(self, record: AnalysisRecord) -> None: ...

    @abstractmethod
    async def get(self, id: str) -> AnalysisRecord | None: ...

    @abstractmethod
    async def update_status(self, id: str, status: str) -> None: ...


class AgentResultRepository(ABC):
    @abstractmethod
    async def save(self, record: AgentResultRecord) -> None: ...

    @abstractmethod
    async def list_by_analysis(self, analysis_id: str) -> list[AgentResultRecord]: ...


class EvidenceRepository(ABC):
    @abstractmethod
    async def save_many(self, records: list[EvidenceRecord]) -> None: ...

    @abstractmethod
    async def list_by_agent_result(self, agent_result_id: str) -> list[EvidenceRecord]: ...


class DecisionResultRepository(ABC):
    @abstractmethod
    async def save(self, record: DecisionResultRecord) -> None: ...

    @abstractmethod
    async def get_by_analysis(self, analysis_id: str) -> DecisionResultRecord | None: ...


class FeedbackRepository(ABC):
    @abstractmethod
    async def save(self, record: FeedbackRecord) -> None: ...

    @abstractmethod
    async def list_by_analysis(self, analysis_id: str) -> list[FeedbackRecord]: ...

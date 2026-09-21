from abc import ABC, abstractmethod

from services.memory.schemas import MemoryRecord


class MemoryRepository(ABC):
    @abstractmethod
    async def save(self, record: MemoryRecord) -> None: ...

    @abstractmethod
    async def list_by_user(self, user_id: str) -> list[MemoryRecord]: ...


class InMemoryMemoryRepository(MemoryRepository):
    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    async def save(self, record: MemoryRecord) -> None:
        self._records.append(record)

    async def list_by_user(self, user_id: str) -> list[MemoryRecord]:
        return [r for r in self._records if r.user_id == user_id]

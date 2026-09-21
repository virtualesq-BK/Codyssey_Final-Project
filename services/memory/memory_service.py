from services.memory.repository import InMemoryMemoryRepository, MemoryRepository
from services.memory.schemas import MemoryRecord


class MemoryService:
    def __init__(self, repository: MemoryRepository | None = None) -> None:
        self.repository = repository or InMemoryMemoryRepository()

    async def save(self, record: MemoryRecord) -> None:
        await self.repository.save(record)

    async def get_user_history(self, user_id: str) -> list[MemoryRecord]:
        return await self.repository.list_by_user(user_id)

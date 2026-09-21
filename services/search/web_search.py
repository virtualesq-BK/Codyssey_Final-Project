from abc import ABC, abstractmethod


class SearchClient(ABC):
    """Placeholder interface for external web search (TODO: implement)."""

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[dict]: ...

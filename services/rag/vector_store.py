import math
from abc import ABC, abstractmethod

from services.rag.schemas import Document, SearchResult


class VectorStore(ABC):
    @abstractmethod
    async def add(self, document: Document, embedding: list[float]) -> None: ...

    @abstractmethod
    async def query(
        self, embedding: list[float], filters: dict | None, top_k: int
    ) -> list[SearchResult]: ...


def _matches(doc: Document, filters: dict | None) -> bool:
    if not filters:
        return True
    for key, expected in filters.items():
        actual = getattr(doc, key, None)
        if actual is None:
            actual = doc.metadata.get(key)
        if actual != expected:
            return False
    return True


def _cosine(a: list[float], b: list[float]) -> float:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._items: list[tuple[Document, list[float]]] = []

    async def add(self, document: Document, embedding: list[float]) -> None:
        self._items.append((document, embedding))

    async def query(self, embedding, filters, top_k) -> list[SearchResult]:
        scored = [
            SearchResult(document=d, score=_cosine(embedding, e))
            for d, e in self._items
            if _matches(d, filters)
        ]
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

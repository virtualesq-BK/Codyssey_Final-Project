from services.rag.embeddings import EmbeddingModel
from services.rag.schemas import SearchResult
from services.rag.vector_store import VectorStore


class Retriever:
    def __init__(self, embeddings: EmbeddingModel, store: VectorStore) -> None:
        self.embeddings = embeddings
        self.store = store

    async def retrieve(
        self, query: str, filters: dict | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        embedding = await self.embeddings.embed(query)
        return await self.store.query(embedding, filters, top_k)

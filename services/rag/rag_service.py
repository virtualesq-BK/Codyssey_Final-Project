from services.rag.embeddings import EmbeddingModel, HashEmbedding
from services.rag.retriever import Retriever
from services.rag.schemas import Document, SearchResult
from services.rag.vector_store import InMemoryVectorStore, VectorStore


class RAGService:
    """Single shared RAG entry point. Agents pass their own query and filters."""

    def __init__(
        self, embeddings: EmbeddingModel | None = None, store: VectorStore | None = None
    ) -> None:
        self.embeddings = embeddings or HashEmbedding()
        self.store = store or InMemoryVectorStore()
        self.retriever = Retriever(self.embeddings, self.store)

    async def add_document(self, document: Document) -> None:
        await self.store.add(document, await self.embeddings.embed(document.content))

    async def search(
        self, query: str, filters: dict | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        return await self.retriever.retrieve(query, filters, top_k)

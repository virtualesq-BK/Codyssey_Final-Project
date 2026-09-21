from services.rag.rag_service import RAGService
from services.rag.schemas import Document


async def _seeded() -> RAGService:
    rag = RAGService()
    await rag.add_document(Document(id="1", title="시장", content="시장 규모 성장률 산업 동향",
                                    source_type="report", metadata={"industry": "fintech"}))
    await rag.add_document(Document(id="2", title="규제", content="법률 규제 정책",
                                    source_type="official", metadata={"industry": "fintech"}))
    return rag


async def test_search_ranks_relevant_document_first():
    results = await (await _seeded()).search("시장 규모 성장률", top_k=2)
    assert results[0].document.id == "1"


async def test_search_filters_and_top_k():
    rag = await _seeded()
    results = await rag.search("규제", filters={"source_type": "official"})
    assert [r.document.id for r in results] == ["2"]
    assert len(await rag.search("규제", top_k=1)) == 1
    assert await rag.search("규제", filters={"source_type": "none"}) == []

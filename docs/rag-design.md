# RAG Design

하나의 `RAGService`를 모든 Agent가 공유합니다. 각 Agent가 자신의 query와 filters를 전달합니다.

- `search(query, filters=None, top_k=5) -> list[SearchResult]`
- 현재 구현: `HashEmbedding`(테스트용) + `InMemoryVectorStore`.
- Decision Agent에는 원문을 전달하지 않고, 각 Agent가 Evidence로 요약한 결과만 전달합니다.

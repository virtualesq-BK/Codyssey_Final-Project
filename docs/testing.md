# Testing

- LLM 응답 문장은 테스트하지 않습니다. status, agent_name, schema 유효성, 필수 필드, evidence 구조, confidence 범위, 에러 처리를 검증합니다.
- `tests/agents`: Agent별 계약 테스트 / `tests/services`: 계산기(결정적)·RAG 검색·메모리·LLM factory
- `tests/integration`: 멀티 에이전트 워크플로 / `tests/e2e`: API health
- 실행: `python -m pytest`

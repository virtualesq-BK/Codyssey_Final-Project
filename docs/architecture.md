# Architecture

## 전체 흐름

```
User
↓
Frontend (apps/web — Next.js)
↓  POST /api/analyze
Backend API (apps/api — FastAPI)
↓
OrchestratorAgent
↓ 병렬 실행
├── MarketAgent         (B 담당)
├── CompetitorAgent     (B 담당)
├── CustomerAgent       (C 담당)
├── BusinessModelAgent  (C 담당)
├── FinancialAgent      (D 담당)
├── RiskAgent           (D 담당)
└── LegalComplianceAgent (E 담당)
↓ 구조화된 AgentResult 만 전달 (RAG 원문 ✗)
DecisionAgent           (A 담당)
↓
DecisionResult
↓  GET /api/analysis/{id}
Frontend
```

## 레이어

| 레이어 | 경로 | 책임 |
|--------|------|------|
| API | `apps/api/` | HTTP 진입점, 비동기 태스크 |
| Agents | `agents/` | 분석 로직 |
| Services | `services/` | LLM / RAG / Memory / Calculation |
| Domain | `domain/` | 공통 Pydantic 스키마 |
| DB | `db/` | Repository 계약 (D 구현) |

## 핵심 원칙

- Agent는 `BaseAgent`를 상속하고 `AgentResult`만 반환합니다.
- Agent끼리 서로 내부를 import하지 않습니다.
- LLM은 `LLMProvider` 인터페이스로만 호출합니다.
- RAG는 `RAGService` 하나를 공유합니다.
- 재무 계산은 `FinancialCalculator` Python으로 수행합니다.
- Decision Agent는 RAG 원문이 아닌 구조화된 Evidence만 받습니다.
- Secret은 환경변수로만 읽습니다.

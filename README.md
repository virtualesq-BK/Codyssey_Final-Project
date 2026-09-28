# AI Business Decision Copilot

사업 아이디어를 입력하면 7개 전문 AI Agent가 독립적으로 분석하고,
Decision Agent가 근거 기반의 종합 보고서를 생성하는 **Multi-Agent Business Decision Support System**입니다.

> ⚠️ **AI 생성 콘텐츠 공시**: 이 서비스는 AI가 생성한 분석 결과를 제공합니다.
> Legal & Compliance 분석은 확정적 법률 자문이 아닙니다. 최종 법률 판단은 전문가에게 문의하십시오.

---

## Workflow

```
User Idea → API → Orchestrator → 7 Agents (병렬) → Decision Agent → Report
```

| Agent | 담당 |
|-------|------|
| Market | B |
| Competitor | B |
| Customer | C |
| Business Model | C |
| Financial | D |
| Risk | D |
| Legal & Compliance | E |
| Decision (종합) | A |
| Orchestrator | A |

---

## 실행 방법

### Backend (Python 3.11+)

```bash
pip install -e ".[dev]"
# 로컬 전용 .env 생성 (절대 커밋하지 않음)
cp .env.example .env
uvicorn apps.api.main:app --reload
```

주요 엔드포인트:
- `GET  /health` — 헬스 체크
- `POST /api/analyze` — 분석 시작 → `analysis_id` 반환
- `GET  /api/analysis/{analysis_id}` — 결과 조회

### Frontend (Node 20+)

```bash
cd apps/web
npm install
npm run dev   # http://localhost:3000
```

---

## 테스트 / 검사

```bash
python -m pytest          # 43개 테스트
python -m ruff check .    # 린트
python -m mypy agents services domain apps db  # 타입 검사
```

---

## API 요청 예시

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "business_idea": "AI 회계 도우미 SaaS",
    "target_customer": "소상공인",
    "country": "KR",
    "price": 29000
  }'
# → {"analysis_id": "...", "status": "accepted"}

curl http://localhost:8000/api/analysis/<analysis_id>
# → {"analysis_id": "...", "status": "completed", "result": {...}}
```

---

## 개발 원칙

- 모든 Agent는 `BaseAgent`를 상속하고 `AgentResult`만 반환합니다.
- Agent끼리 내부 구현을 직접 import하지 않습니다.
- LLM은 `LLMProvider` 인터페이스로만 호출합니다 (SDK 직접 사용 금지).
- RAG는 `services/rag`의 `RAGService` 하나를 공유합니다.
- 재무 계산은 `services/calculation`의 Python이 수행합니다.
- Secret은 환경변수로만 읽고 `.env`는 커밋하지 않습니다.
- Interface 변경 시 `docs/agent-interface.md`에 이유를 기록합니다.

자세한 내용 → [docs/](docs/)

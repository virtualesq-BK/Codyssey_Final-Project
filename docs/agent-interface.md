# Agent Interface 계약

> **변경 이력**: `2026-09-29` — Legal & Compliance Agent 추가, Evidence 필드 확장,
> DecisionResult에 `legal_compliance_assessment` 추가.
> 기존 Agent 코드는 영향 없음 (신규 필드 모두 선택).

---

## BaseAgent

```python
class BaseAgent:
    name: str
    async def run(self, input_data: BusinessIdea) -> AgentResult: ...
```

- 반환값은 **항상** `AgentResult`.
- Agent끼리 서로를 import하지 않습니다.
- 공통 기능은 `services/`, 공통 스키마는 `domain/`.

---

## AgentResult

| 필드 | 타입 | 필수 |
|------|------|------|
| agent_name | str | ✅ |
| status | AgentStatus | ✅ |
| summary | str | |
| findings | list[str] | |
| evidence | list[Evidence] | |
| recommendations | list[str] | |
| confidence | float 0–1 | |
| metadata | dict | |

**상태값**: `success` / `partial` / `failed` / `not_implemented`

---

## Evidence

| 필드 | 타입 | 비고 |
|------|------|------|
| source_title | str | 필수 |
| source_type | str | 필수 |
| url | str? | |
| claim | str | 필수 |
| published_at | date? | |
| relevance | float 0–1 | |
| **source_level** | str? | Legal Agent 전용 (예: "statute") |
| **citation** | str? | Legal Agent 전용 (예: "공정거래법 제3조") |
| **retrieved_at** | datetime? | Legal Agent 전용 |

`source_level`, `citation`, `retrieved_at` 은 **Legal & Compliance Agent 전용** 선택 필드입니다.
다른 Agent는 채우지 않아도 됩니다.

---

## DecisionResult

| 필드 | 비고 |
|------|------|
| executive_summary | |
| market_assessment | Market Agent 요약 |
| customer_assessment | Customer Agent 요약 |
| competition_assessment | Competitor Agent 요약 |
| business_model_assessment | BusinessModel Agent 요약 |
| financial_assessment | Financial Agent 요약 |
| risk_assessment | Risk Agent 요약 |
| **legal_compliance_assessment** | Legal & Compliance Agent 요약 (신규) |
| key_findings | |
| open_questions | |
| action_plan | |
| confidence | float 0–1 |
| evidence | list[Evidence] |

---

## BusinessIdea

| 필드 | 비고 |
|------|------|
| title | 필수 |
| description | |
| target_customer | |
| industry | |
| geography | 기존 필드 유지 |
| **country** | API `/api/analyze` 의 `country` 파라미터 매핑 (신규) |
| business_model | |
| **price** | 예상 가격, float? (신규) |
| additional_context | dict |

---

## 파이프라인 원칙

```
Document → Evidence → Finding → Recommendation
```

- Decision Agent에 RAG 원문 전체를 전달하지 않습니다.
- 근거 부족 시: `"INSUFFICIENT_EVIDENCE"` 또는 `"추가 검증 필요"`.

---

## AI 윤리 / Legal Boundary

- 서비스 결과에 AI 생성 콘텐츠임을 명시합니다.
- **Legal & Compliance Agent** 는 법률 자문을 확정적으로 제공하는 AI 변호사가 아닙니다.
  표현: *"사업 의사결정 과정에서 확인해야 할 법률·규제 리스크와 관련 근거를 탐색·정리하는 AI Agent"*
  금지 표현: AI 변호사 / 법률 판단 확정 / 법적 승소 보장 / 법률 자문 대체

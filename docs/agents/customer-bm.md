# C 결과 설계서 — Customer Agent · Business Model Agent

> 담당: C (great-opportunity) · 상태: **초안 v0.1** · 최종 수정: 2026-10-06
> 이 문서는 두 에이전트가 **무엇을 받아서 무엇을 돌려주는지**, 그리고 **좋은 결과의 기준**을 정한다.
> 공통 계약(`BaseAgent`, `AgentResult`, `Evidence`)은 바꾸지 않는다. 구조화된 값은 `AgentResult.metadata`에 넣는다.

---

## 1. 역할 범위

| 에이전트 | 답하는 질문 | 하는 것 | 하지 않는 것 (담당) |
| --- | --- | --- | --- |
| **Customer** (`customer`) | 누가, 어떤 상황에서, 얼마나 아파하나? | 문제 진술, JTBD, 현재 대안, 세그먼트·비치헤드, 사용자/지불자 구분, 페르소나, 구매 동기·장벽, 검증 필요 가설 | 시장 규모 계산 (B·Market), 경쟁사 조사 (B·Competitor) |
| **Business Model** (`business_model`) | 어떻게 돈을 버나? | 가치 제안, 수익 모델 후보 비교, 가격 제안과 근거, 무료/유료 구분, 채널, 고객 확보, 핵심 자원·활동·파트너, 비용 동인 | 매출·CAC·LTV·BEP 계산 (D·Financial), 법·규제 (Legal) |

**분석 기준 담당**: "좋은 고객·BM 분석"의 기준(5장)을 C가 관리한다. 프롬프트 수정과 사용자 테스트 평가의 기준이 된다.

---

## 2. 입력

두 에이전트 모두 `BusinessIdea`만 받는다. 오케스트레이터가 모든 에이전트를 **동시에** 실행하므로 BM은 Customer 결과를 받지 못한다 (→ 8장 열린 질문 1).

| 필드 | 사용처 |
| --- | --- |
| `title`, `description` | 둘 다 — 분석 대상 |
| `target_customer` | Customer — 출발 가설. 비어 있으면 후보 세그먼트를 직접 제안 |
| `industry`, `geography`/`country` | 둘 다 — RAG 검색 필터, 지역 맥락 |
| `business_model` | BM — 사용자가 생각한 수익 모델 (후보 비교에 포함) |
| `price` | BM — 사용자가 생각한 가격 (비어 있으면 제안) |
| `additional_context` | 둘 다 — 인터뷰 메모 등 (있으면 근거 등급 A 후보) |

---

## 3. 출력 — 공통 규칙 (`AgentResult`)

| 필드 | 규칙 |
| --- | --- |
| `agent_name` | `"customer"` / `"business_model"` |
| `status` | `success` = 필수 칸 모두 채움 · `partial` = LLM 응답을 해석 못 했거나 필수 칸 일부 누락 · `failed` = 예외 발생 (`failed_result`) |
| `summary` | 2~3문장. Decision Agent가 `customer_assessment` / `business_model_assessment`로 쓴다 |
| `findings` | 핵심 발견 **최대 5개**, 각 1문장, 문장 끝에 근거 등급 표기. 예: `"사용자(교사)와 지불자(교감·행정실)가 다르다 [C]"` |
| `evidence` | RAG·검색에서 나온 근거만. 지어낸 출처 금지 |
| `recommendations` | 다음에 검증할 행동 최대 3개 (누가·무엇을·성공 기준) |
| `confidence` | **코드로 계산**: 핵심 주장 근거 등급 비율 기반 (A=1.0, B=0.75, C=0.5, D=0.25 평균). LLM이 정하지 않는다 |
| `metadata` | 4장 스키마. `metadata["schema_version"] = "c-0.1"` |

### 근거 등급 (보고서 구성안과 동일)

| 등급 | 뜻 | 예 |
| --- | --- | --- |
| A | 고객에게서 직접 수집한 실데이터 | 인터뷰, 실제 설문 (`additional_context`로 들어온 것) |
| B | 출처 확인된 공개 통계·공식 자료 | 통계청, 부처 자료 (RAG 결과) |
| C | 벤치마크·유사 사례 기반 추정 | 업계 평균, 비슷한 서비스 사례 |
| D | AI 추정 또는 근거 없는 가정 | 근거 없이 생성한 값 — **결론의 단독 근거로 쓰지 않는다** |

### 지어내지 않기

- 입력·근거에 없는 숫자는 만들지 않는다. 필요하면 범위로 쓰고 등급 D를 붙이거나 `"INSUFFICIENT_EVIDENCE"`로 둔다.
- 페르소나는 항상 `is_hypothetical: true` — 실제 인터뷰가 아니면 가상 인물임을 명시.
- 점수 합계·정렬처럼 계산 가능한 것은 LLM이 아니라 코드가 한다 (세그먼트 합계, confidence).

---

## 4. `metadata` 스키마

### 4-1. Customer

```jsonc
{
  "schema_version": "c-0.1",
  "problem_statement": {            // 누가 / 언제 / 무엇 때문에 / 어떤 손실 — 한 문장
    "text": "...",
    "frequency": "학기당 1~2회",
    "grade": "B"
  },
  "jtbd": {
    "when": "...", "want": "...", "so_that": "...",
    "functional": "...", "emotional": "...", "social": "..."
  },
  "alternatives": [                 // 최소 2개, "아무것도 안 함" 반드시 포함
    { "method": "...", "cost_or_pain": "...", "pain_score": 4, "grade": "C" }
  ],
  "segments": [                     // 각 1~5점, total은 코드가 계산
    { "name": "...", "size": 4, "pain": 5, "willingness_to_pay": 2, "reach": 4, "total": 15, "grade": "C" }
  ],
  "beachhead": { "segment": "...", "reason": "..." },
  "user_vs_payer": { "user": "...", "payer": "...", "same": false },
  "personas": [                     // 1~2명
    { "name": "...", "profile": "...", "day": "...", "worst_moment": "...",
      "tools": ["..."], "buying_power": "...", "is_hypothetical": true }
  ],
  "purchase_drivers": ["..."],
  "purchase_barriers": ["..."],
  "hypotheses": [                   // 아직 근거가 약한 것 — 보고서 '검증 필요 가설'
    { "id": "H1", "statement": "...", "grade": "D", "validation": "교사 8명 실측 (2주)" }
  ]
}
```

필수 칸: `problem_statement`, `jtbd`, `alternatives`(2개 이상), `segments`(1개 이상), `beachhead`, `user_vs_payer`, `personas`(1개 이상), `hypotheses`

### 4-2. Business Model

```jsonc
{
  "schema_version": "c-0.1",
  "value_proposition": {            // "누구에게 / 무슨 문제를 / 무엇으로 / 기존 대안과 달리"
    "for_whom": "...", "problem": "...", "offer": "...", "unlike": "..."
  },
  "revenue_model_candidates": [     // 2~4개, 사용자가 입력한 모델이 있으면 포함
    { "model": "학교 단위 연간 구독", "fit": 0.92, "rationale": "...", "grade": "B" }
  ],
  "chosen_model": "학교 단위 연간 구독",
  "pricing": {
    "price_krw": 1200000,
    "billing_period": "year",       // "month" | "year" | "one_time" | "per_use"
    "unit": "school",               // 무엇 1개당 가격인가: user / school / seat / case ...
    "range_low_krw": 990000,
    "range_high_krw": 1510000,
    "rationale": "...",
    "grade": "D"
  },
  "price_ladder": [                 // 선택
    { "plan": "진입", "price_krw": 990000, "includes": "...", "target": "..." }
  ],
  "free_vs_paid": { "free": ["..."], "paid": ["..."] },
  "channels": [ { "channel": "...", "role": "인지 | 구매 | 전달", "grade": "C" } ],
  "acquisition": [ { "tactic": "...", "target_segment": "...", "grade": "C" } ],
  "key_resources": ["..."],
  "key_activities": ["..."],
  "key_partners": ["..."],
  "cost_drivers": ["..."],          // 금액 계산은 D. 여기선 항목만
  "handoff_to_financial": {         // D와 합의할 칸 (6장)
    "price_krw": 1200000,
    "billing_period": "year",
    "unit": "school",
    "payer_type": "B2B"             // "B2C" | "B2B" | "B2G"
  }
}
```

필수 칸: `value_proposition`, `revenue_model_candidates`(2개 이상), `chosen_model`, `pricing`, `channels`, `handoff_to_financial`

---

## 5. 좋은 분석의 기준 (품질 체크리스트)

프롬프트 수정·리뷰·사용자 테스트에서 이 표로 판단한다. 자동 검사 가능한 것은 코드로 검사한다.

| # | 기준 | 대상 | 자동 검사 |
| --- | --- | --- | --- |
| 1 | 문제 진술에 누가·언제·무엇 때문에·어떤 손실이 모두 있다 | Customer | |
| 2 | 사용자와 지불자를 구분했다 (같으면 같다고 명시) | Customer | ✅ `user_vs_payer` 존재 |
| 3 | 현재 대안에 "아무것도 안 함"이 포함됐다 | Customer | ✅ |
| 4 | 비치헤드 선택 이유가 세그먼트 점수와 일치한다 | Customer | ✅ 최고점 또는 사유 명시 |
| 5 | 페르소나가 구체적이고 가상임을 밝혔다 | Customer | ✅ `is_hypothetical` |
| 6 | 가격에 금액·기간·단위·근거·등급이 다 있다 | BM | ✅ |
| 7 | 가격 제안이 범위(low~high) 안에 있다 | BM | ✅ |
| 8 | 수익 모델 후보를 2개 이상 비교했다 | BM | ✅ |
| 9 | 모든 숫자에 근거 등급이 있고, D등급만으로 결론을 내지 않았다 | 둘 다 | ✅ 등급 존재 |
| 10 | findings가 5개 이하, 각 1문장이다 | 둘 다 | ✅ |
| 11 | 비개발자 창업자가 읽고 바로 이해할 수 있다 | 둘 다 | 사용자 테스트 |

---

## 6. 다른 역할과의 접점

| 상대 | 주고받는 것 | 합의 필요 |
| --- | --- | --- |
| **D (Financial)** | BM `handoff_to_financial` → 재무 계산 입력 | 칸 이름·단위(원, 기간, 단위) 확정. 예상 고객 수는 누가 정하나? |
| **A (Decision·Orchestrator)** | `summary` → `customer_assessment`, `business_model_assessment` / `metadata` 구조 | metadata 사용 방식, 실행 순서 (8장 1) |
| **B (RAG)** | Customer: 인구·통계 자료 검색 / BM: 유사 서비스 가격·수익 모델 검색 | 검색 필터(metadata) 이름, 수집 자료 범위 |
| **E (화면)** | 페르소나 카드, JTBD 카드, 세그먼트 점수표, 가격 사다리 표시 | 화면에 보여줄 칸 |
| **DB** | `agent_results.metadata`(jsonb)에 그대로 저장 | 없음 |

---

## 7. 기준 예시 (Golden example)

입력: 다문화 학생 한국어 지원 SaaS. 출처: 팀 내부 `사업분석보고서_다문화한국어SaaS_v0.1` 1장·4장 요약. 프롬프트 품질을 볼 때 이 수준이 목표다.

**Customer (요약)**

- 문제 진술: 담임을 겸하는 다문화 담당 교사가 학기말 교육청 제출 자료를 만들 때, 학생 15~30명의 한국어 수준·진도 기록이 여러 문서에 흩어져 있어 자료를 모으는 데만 하루 이상 쓴다. [B]
- JTBD: 학기말 제출 자료를 만들어야 할 때 → 평소 기록이 그대로 보고 양식이 되기를 원한다 → 밤새우지 않고 누락 없이 제출한다.
- 대안: 엑셀 여러 개(4/5) · 한글 문서(4/5) · 공공 진단 시스템(3/5) · 외부 기관 연계(3/5) · **아무것도 안 함 — 학기말에 몰아서 작성(5/5)**
- 세그먼트: 겸임 다문화 담당 교사(15) > 교감·교무(14) > 한국어학급 담당 교사(12) …
- 비치헤드: 겸임 다문화 담당 교사(초등). 단, 지불 점수 2점 → **사용자와 지불자 분리 필요**
- 사용자 vs 지불자: 교사 / 교감·행정실 (다름)
- 페르소나(가상): 초등 5년차 담임, 다문화 업무 겸임 2년차, 담당 18명. 가장 싫은 순간 = 학기말에 넉 달치 수업을 기억에 의존해 복원할 때. 구매 권한 없음.
- 가설: H1 작성 1회 4시간 이상 [D] · H3 교감·행정실이 연 120만 원 집행 가능 [C] · H4 학교가 외부 저장을 허용 [D]

**Business Model (요약)**

- 수익 모델 후보: 학교 단위 연간 구독(0.92, B) · 교육청 일괄 공급(0.78, C) · 보고서 건당 과금(0.41, C) · 교사 개인 구독(0.25, D)
- 선택: 학교 단위 연간 구독 — 다문화교육 예산·결재선에 그대로 얹힘
- 가격: 연 1,200,000원 / 학교, 범위 990,000~1,510,000원 [D — 가상 응답 기반, 실고객 확인 필요]
- 가격 사다리: 진입 99만 / 표준 120만 / 확장 151만
- handoff: `{price_krw: 1200000, billing_period: "year", unit: "school", payer_type: "B2B"}`

이 예시에서 배울 점: **가장 중요한 발견("쓰는 사람과 사는 사람이 다르다")이 고객 분석에서 나와 BM과 최종 판정(Pivot)까지 이어진다.** C의 분석이 팀 결론을 바꿀 수 있어야 한다.

---

## 8. 열린 질문

1. **실행 순서**: BM이 Customer의 비치헤드·지불자를 못 보고 따로 분석하면 둘이 엇갈릴 수 있다. Customer → BM 순서로 바꾸거나, BM이 Customer 결과를 입력으로 받는 방법을 A와 논의 (GitHub Issue 예정).
2. **예상 고객 수**: 재무 계산에 필요한 고객 수를 BM이 낼지 D가 낼지.
3. **가격 정밀 분석**: 보고서 구성안의 PSM·매출 곡선은 실제 설문 데이터가 필요 → MVP에서는 범위 제안 + 등급 D 표시로 대체.
4. **출력 언어**: 한국어 고정 여부.

---

## 9. 구현 계획

1. 프롬프트: 시스템 프롬프트에 4장 스키마 + 3장 규칙 포함, JSON만 응답하도록
2. 파싱: JSON 추출 → Pydantic으로 검증 → 실패 시 `partial` (테스트용 `FakeLLMProvider`는 `"fake response"`를 돌려주므로 반드시 처리)
3. 후처리(코드): 세그먼트 합계, confidence, 자동 검사 항목(5장 ✅)
4. RAG: `rag.search(query, filters)` 결과를 `Evidence`로 변환 (rag가 없으면 근거 없이 진행, 등급 하향)
5. 테스트: 기존 계약 테스트 유지 + 정상 JSON 응답 / 깨진 응답 / 필수 칸 누락 케이스 추가
6. 기준 예시(7장)로 실제 LLM 결과 비교 → 프롬프트 개선

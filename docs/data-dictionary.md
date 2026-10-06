# 데이터 사전 (Agent 결과 칸 정의)

> 상태: **초안 v0.1** (C 작성, 팀 리뷰 전) · 최종 수정: 2026-10-06
> 목적: 에이전트가 늘어나도 칸 이름·단위·뜻이 헷갈리지 않게, **모든 에이전트 결과의 칸을 한곳에서** 정의한다.
> 각 담당자는 자기 에이전트 섹션을 채운다. 공통 규칙(1~3장) 변경은 GitHub Issue로.

## 목차
1. [이름 규칙](#1-이름-규칙)
2. [공통 껍데기 — AgentResult](#2-공통-껍데기--agentresult)
3. [공통 값 — 등급·점수·단위](#3-공통-값--등급점수단위)
4. [Customer Agent](#4-customer-agent-c) · [Business Model Agent](#5-business-model-agent-c)
6. [에이전트 간 전달](#6-에이전트-간-전달)
7. [헷갈리기 쉬운 용어](#7-헷갈리기-쉬운-용어)
8. [변경 제안 (v0.2 후보)](#8-변경-제안-v02-후보)
9. [다른 에이전트 (담당자 작성)](#9-다른-에이전트-담당자-작성)

---

## 1. 이름 규칙

| 규칙 | 예 | 이유 |
| --- | --- | --- |
| 에이전트별 분석은 **그 에이전트의 `metadata` 안에만** 둔다 | `customer.metadata.segments` | 칸 이름이 겹쳐도 어느 에이전트 것인지 항상 구분됨 |
| 다른 에이전트에 넘길 때는 **`<agent>_analysis`** 키로 감싼다 | `additional_context.customer_analysis` | 받는 쪽에서 출처가 바로 보임 |
| 칸 이름은 영어 `snake_case` | `problem_statement` | 팀 코드 규칙 |
| 금액은 원화 정수 + **`_krw`** | `price_krw: 1200000` | 단위를 이름에서 바로 앎 |
| 정해진 선택지는 영어 소문자 | `billing_period: "year"` | 화면에서 한국어로 바꿔 표시 |
| 참/거짓은 `is_` / `has_` / `used_` | `is_hypothetical` | 읽으면 질문처럼 보이게 |
| 다른 칸을 가리킬 때는 **이름 대신 id** (→ 8장 제안 1) | `beachhead.segment_id` | 이름 문자열 비교는 깨지기 쉬움 |
| 구조 버전 표시 | `schema_version: "c-0.1"` | 칸이 바뀌어도 옛 결과를 구분 |

---

## 2. 공통 껍데기 — `AgentResult`

모든 에이전트가 같은 모양으로 돌려준다 (`domain/agent_result.py`, A 관리).

| 칸 | 타입 | 뜻 | 채움 |
| --- | --- | --- | --- |
| `agent_name` | str | 에이전트 이름 (`customer`, `business_model` …) | 코드 |
| `status` | `success` · `partial` · `failed` · `not_implemented` | 실행 결과 | 코드 |
| `summary` | str | 2~3문장 요약. Decision이 `<agent>_assessment`로 사용 | AI |
| `findings` | str[] | 핵심 발견 최대 5개, 끝에 `[A~D]` 등급 | AI (+코드가 등급 표기) |
| `evidence` | Evidence[] | RAG에서 나온 근거 | 코드 |
| `recommendations` | str[] | 다음에 검증할 행동 최대 3개 | AI |
| `confidence` | 0~1 | 근거 등급 평균 (A=1, B=.75, C=.5, D=.25) | **코드** |
| `metadata` | dict | 에이전트별 분석 본문 (4장~) | AI + 코드 |

---

## 3. 공통 값 — 등급·점수·단위

| 값 | 범위 | 뜻 | 쓰는 곳 |
| --- | --- | --- | --- |
| `grade` | `A` `B` `C` `D` | 근거 등급. A 실고객 데이터 · B 공개 통계 · C 벤치마크 추정 · D 근거 없음 | 모든 주장 |
| `confidence` | 0.0~1.0 | 결과 전체의 신뢰도 (코드 계산) | AgentResult |
| `fit` | 0.0~1.0 | 수익 모델 후보의 적합도 | BM |
| 세그먼트 점수 | 정수 1~5 | 규모·고통·지불 의사·도달 | Customer |
| `pain_score` | 정수 1~5 | 대안의 불편 정도 | Customer |
| 금액 | 원화 정수 | `_krw` 칸 | BM |
| 결제 주기 | `month` `year` `one_time` `per_use` | | BM |
| 지불 주체 | `B2C` `B2B` `B2G` | 개인 · 민간 기관 · 공공 예산 | BM |

> **주의**: 0~1 비율(`fit`, `confidence`)과 1~5 점수를 섞지 말 것.

---

## 4. Customer Agent (C)

`agent_name: "customer"` · 답하는 질문: **누가, 어떤 상황에서, 얼마나 아파하나?**

| 칸 | 타입 | 뜻 | 채움 | 화면 | 쓰는 곳 |
| --- | --- | --- | --- | --- | --- |
| `problem_statement` | `{text, frequency, grade}` | 누가·언제·무엇 때문에·어떤 손실 | AI | 문제 | BM, Decision |
| `jtbd` | `{when, want, so_that, functional, emotional, social}` | 고객이 해결하려는 일 | AI | JTBD 흐름 | |
| `alternatives[]` | `{method, cost_or_pain, pain_score, grade}` | 지금 고객이 쓰는 방법 (항상 "아무것도 안 함" 포함) | AI | 현재 대안 | |
| `segments[]` | `{name, size, pain, willingness_to_pay, reach, total, grade}` | 고객 세그먼트와 점수 | AI · **`total`은 코드** | 세그먼트 점수표 | BM |
| `beachhead` | `{segment, reason}` | 첫 공략 세그먼트 | AI | 강조 줄 | **BM** |
| `user_vs_payer` | `{user, payer, same}` | 쓰는 사람과 돈 내는 사람 | AI | 사용자 vs 지불자 | **BM** |
| `personas[]` | `{name, profile, day, worst_moment, tools, buying_power, is_hypothetical}` | 대표 고객 1~2명 | AI · **`is_hypothetical`은 코드가 강제** | 페르소나 카드 | |
| `purchase_drivers[]` | str | 사는 이유 | AI | 구매 동기 | BM |
| `purchase_barriers[]` | str | 안 사는 이유 | AI | 구매 장벽 | BM |
| `hypotheses[]` | `{id, statement, grade, validation}` | 근거가 약한 핵심 가정과 검증 방법 | AI | 가설 | BM, Decision |
| `quality_checks` | `{칸: bool}` | 자동 품질 검사 | **코드** | ✓/✗ | |

---

## 5. Business Model Agent (C)

`agent_name: "business_model"` · 답하는 질문: **누구에게, 어떤 방식으로, 얼마를 받나?**

| 칸 | 타입 | 뜻 | 채움 | 화면 | 쓰는 곳 |
| --- | --- | --- | --- | --- | --- |
| `value_proposition` | `{for_whom, problem, offer, unlike}` | 가치 제안 한 문장 | AI | 가치 제안 | Decision |
| `revenue_model_candidates[]` | `{model, fit, rationale, grade}` | 수익 모델 후보 2~4개 | AI | 후보 비교 | |
| `chosen_model` | str | 선택한 후보 (`model`과 같은 값) | AI | 선택 강조 | |
| `payer_type` | `B2C`·`B2B`·`B2G` | 지불 주체 | AI | 배지 | D |
| `pricing` | `{price_krw, billing_period, unit, range_low_krw, range_high_krw, rationale, grade}` | 제안 가격과 범위 | AI | 가격 카드 | D |
| `price_ladder[]` | `{plan, price_krw, includes, target}` | 요금제 | AI | 요금제 표 | |
| `free_vs_paid` | `{free[], paid[]}` | 무료·유료 기능 | AI | 무료/유료 | |
| `channels[]` | `{channel, role, grade}` | 판매·전달 경로 | AI | 채널 | |
| `acquisition[]` | `{tactic, target_segment, grade}` | 고객 확보 방법 | AI | 고객 확보 | |
| `key_resources[]` · `key_activities[]` · `key_partners[]` | str | 핵심 자원·활동·파트너 | AI | 핵심 요소 | |
| `cost_drivers[]` | str | 주요 비용 **항목** (금액 계산은 D) | AI | 주요 비용 | D |
| `handoff_to_financial` | 6장 | D에게 넘기는 값 | **코드** | D에게 넘길 값 | **D** |
| `used_upstream` | str[] | 반영한 앞 단계 결과 (`customer_analysis` …) | **코드** | 안내 문구 | |
| `quality_checks` | `{칸: bool}` | 자동 품질 검사 | **코드** | ✓/✗ | |

---

## 6. 에이전트 간 전달

기획서 원안 순서: **1단계 Market·Customer·Competitor → 2단계 Business Model → 3단계 Financial·Risk → Decision**
(현재 오케스트레이터는 전부 동시 실행 — 단계별 실행은 A에게 Issue 예정)

### Customer → Business Model
`BusinessIdea.additional_context["customer_analysis"]` = Customer의 `metadata`.
BM이 실제로 읽는 칸: `problem_statement`, `beachhead`, `user_vs_payer`, `segments`, `purchase_drivers`, `purchase_barriers`, `hypotheses`.

### Business Model → Financial (D) — ⚠️ 합의 필요

BM이 내보내는 값:

| `handoff_to_financial` | 예 |
| --- | --- |
| `price_krw` | 1800000 |
| `billing_period` | `"year"` |
| `unit` | `"school"` |
| `payer_type` | `"B2G"` |

D의 계산기 입력(`services/calculation/schemas.py` `FinancialInputs`)과 맞춰 보면:

| D가 필요한 칸 | BM이 줄 수 있나 | 문제 |
| --- | --- | --- |
| `price` | ✅ `price_krw` | — |
| `avg_revenue_per_customer_month` | ⚠️ | **D는 월 기준인데 BM은 연 가격** → 월 환산 필요 (연 180만 → 월 15만) |
| `new_customers`, `units_sold` | ❌ | 예상 고객 수를 누가 낼지 미정 |
| `unit_variable_cost`, `fixed_costs`, `marketing_spend` | ❌ | BM은 비용 **항목**만 줌. 금액 추정은 D |
| `gross_margin_pct` | ❌ | D 계산기에서는 **0~1 비율**인데 이름은 `_pct` → 헷갈림 주의 |

---

## 7. 헷갈리기 쉬운 용어

에이전트가 늘어나면 같은 단어가 다른 뜻으로 쓰인다. 아래처럼 구분한다.

| 단어 | 이 뜻일 때 | 칸 | 다른 뜻일 때 |
| --- | --- | --- | --- |
| 세그먼트 | 공략 우선순위를 매긴 **고객 집단** | `customer.segments` | 시장 규모를 나눈 구간 → Market에서는 다른 이름 권장 (예: `market_tiers`) |
| 대안 | 고객이 **지금 문제를 푸는 방법** (아무것도 안 함 포함) | `customer.alternatives` | 경쟁 서비스·대체재 → Competitor (`competitors`, `substitutes`) |
| 지불자 | 고객 분석에서 **누가** 돈을 내나 (서술) | `customer.user_vs_payer.payer` | 지불 주체 **유형** (`B2C/B2B/B2G`) → `business_model.payer_type` |
| 가격 | **우리** 제안 가격 | `business_model.pricing` | 경쟁사 가격 → Competitor |
| 채널 | 판매·전달 경로 | `business_model.channels` | GTM 실행 계획 → 별도 |
| 가설 | 근거가 약해 **검증해야 할** 가정 | `<agent>.hypotheses` | 확정된 입력값 → (향후) 가정 레지스터 |
| 신뢰도 / 적합도 / 관련도 | 결과 전체 / 수익 모델 / 검색 결과 | `confidence` / `fit` / `evidence.relevance` | 셋 다 0~1이지만 뜻이 다름 |
| 등급 | 근거 등급 A~D | `grade` | 법령 위계 → Legal의 `source_level` |

---

## 8. 변경 제안 (v0.2 후보)

| # | 제안 | 이유 | 영향 |
| --- | --- | --- | --- |
| 1 | `segments[]`에 `id` 추가, `beachhead.segment` → `beachhead.segment_id` | 지금은 이름 문자열이 정확히 같아야 연결됨 (AI가 글자 하나만 달리 써도 끊김) | Customer 스키마·프롬프트·뷰어 |
| 2 | `handoff_to_financial`에 `monthly_equivalent_krw` 추가 (코드 계산) | D 계산기가 월 기준 (6장) | BM 코드, D와 합의 |
| 3 | `grade`, `GradedText`, `Hypothesis`를 모든 에이전트 공통 모양으로 | Decision이 모든 에이전트의 가설·발견을 한 번에 모으기 쉬움 | `domain/` 변경 → A와 Issue |
| 4 | D 계산기의 `gross_margin_pct`(0~1) → `gross_margin_ratio` | `_pct`는 보통 0~100으로 읽힘 | D 코드 |

---

## 9. 다른 에이전트 (담당자 작성)

| 에이전트 | 담당 | 상태 |
| --- | --- | --- |
| Market | B | 미작성 |
| Competitor | B | 미작성 |
| Financial | D | 미작성 — 6장 전달 칸 합의부터 |
| Risk | D | 미작성 |
| Legal & Compliance | E | 미작성 (`source_level`, `citation` 사용) |
| Decision · Orchestrator | A | 미작성 |

작성 형식: 4·5장처럼 `칸 | 타입 | 뜻 | 채움 | 화면 | 쓰는 곳` 표 하나.

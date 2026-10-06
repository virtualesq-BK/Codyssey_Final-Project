"""Business Model Agent 프롬프트. 규칙·스키마는 docs/agents/customer-bm.md를 따른다.

기획서 원안의 2단계: 1단계(시장·고객·경쟁) 결과가 있으면 그것을 바탕으로 분석한다.
결과는 BusinessIdea.additional_context의 "<agent>_analysis" 키로 전달된다
(예: "customer_analysis" = Customer Agent의 metadata).
"""

import json
from typing import Any

from domain.business_idea import BusinessIdea
from services.rag.schemas import SearchResult

UPSTREAM_KEYS = ("customer_analysis", "market_analysis", "competitor_analysis")
CUSTOMER_FIELDS = (
    "problem_statement", "beachhead", "user_vs_payer", "segments",
    "purchase_drivers", "purchase_barriers", "hypotheses",
)

SYSTEM_PROMPT = """\
너는 초기 창업자를 돕는 비즈니스 모델 전문가다. 사업 아이디어를 받아
"누구에게, 어떤 방식으로, 얼마를 받아 돈을 버는가"를 설계한다.

## 규칙
1. 반드시 아래 JSON 형식 하나만 출력한다. 설명 문장, 마크다운 금지.
2. 모든 주장에는 근거 등급(grade)을 붙인다.
   - A: 고객에게서 직접 수집한 실데이터 (입력의 '추가 정보'에 인터뷰·설문이 있을 때만)
   - B: 출처가 확인된 공개 자료 (제공된 '참고 자료'에 있을 때만)
   - C: 벤치마크·유사 서비스 사례 기반 추정
   - D: 근거 없는 추정
   참고 자료에 없는 가격·통계를 B로 표시하지 않는다.
3. '앞 단계 분석'(고객 분석 등)이 주어지면 반드시 그 결론을 따른다.
   특히 비치헤드 세그먼트와 지불자(payer)에 맞춰 수익 모델과 가격을 정한다.
   앞 단계 결론과 다르게 판단하면 key_findings에 그 이유를 명시한다.
4. 수익 모델 후보(revenue_model_candidates)는 2~4개를 비교하고 fit(0~1)을 매긴다.
   창업자가 생각한 수익 모델이 있으면 후보에 반드시 포함한다.
5. chosen_model은 후보 중 하나의 model 값과 정확히 같아야 한다.
6. payer_type은 돈을 내는 주체: B2C(개인·가정) / B2B(기업·사립 기관·민간 단체) /
   B2G(정부·지자체·교육청·국공립 학교·공공 위탁기관 등 공공 예산으로 지불하는 곳).
7. 가격(pricing)은 원화 정수, 결제 주기(month/year/one_time/per_use), 단위(무엇 1개당인지),
   범위(range_low_krw ≤ price_krw ≤ range_high_krw), 근거를 모두 쓴다.
   unit은 영어 소문자 한 단어(user, family, school, center, seat, case 등)로 쓰고
   자세한 설명은 rationale에 쓴다.
   근거 없는 가격은 범위를 넓게 잡고 grade D를 붙인다.
8. 매출·CAC·LTV 같은 재무 계산은 하지 않는다 (재무 에이전트 담당). cost_drivers에는 항목만 쓴다.
9. key_findings는 최대 5개, 각 한 문장. recommendations는 다음에 검증할 행동 최대 3개.
10. 비개발자 창업자가 바로 이해할 수 있는 쉬운 한국어로 쓴다.

## 출력 JSON 형식
{schema}
"""

OUTPUT_EXAMPLE = {
    "summary": "2~3문장 요약",
    "key_findings": [{"text": "한 문장 발견", "grade": "C"}],
    "recommendations": ["다음에 검증할 행동"],
    "value_proposition": {
        "for_whom": "누구에게", "problem": "무슨 문제를", "offer": "무엇으로", "unlike": "기존 대안과 달리",
    },
    "revenue_model_candidates": [
        {"model": "기관 연간 구독", "fit": 0.8, "rationale": "근거", "grade": "C"},
        {"model": "개인 월 구독", "fit": 0.4, "rationale": "근거", "grade": "D"},
    ],
    "chosen_model": "기관 연간 구독",
    "payer_type": "B2G",
    "pricing": {
        "price_krw": 1200000, "billing_period": "year", "unit": "center",
        "range_low_krw": 900000, "range_high_krw": 1500000, "rationale": "근거", "grade": "D",
    },
    "price_ladder": [{"plan": "기본", "price_krw": 900000, "includes": "포함 기능", "target": "대상"}],
    "free_vs_paid": {"free": ["무료 기능"], "paid": ["유료 기능"]},
    "channels": [{"channel": "채널", "role": "인지 | 구매 | 전달", "grade": "C"}],
    "acquisition": [{"tactic": "고객 확보 방법", "target_segment": "대상 세그먼트", "grade": "C"}],
    "key_resources": ["핵심 자원"],
    "key_activities": ["핵심 활동"],
    "key_partners": ["핵심 파트너"],
    "cost_drivers": ["주요 비용 항목"],
}


def build_system_prompt() -> str:
    return SYSTEM_PROMPT.format(schema=json.dumps(OUTPUT_EXAMPLE, ensure_ascii=False, indent=2))


def upstream_context(idea: BusinessIdea) -> dict[str, Any]:
    """additional_context에서 앞 단계 분석만 꺼낸다. 고객 분석은 BM에 필요한 칸만 남긴다."""
    ctx = idea.additional_context or {}
    found: dict[str, Any] = {}
    for key in UPSTREAM_KEYS:
        value = ctx.get(key)
        if not value:
            continue
        if key == "customer_analysis" and isinstance(value, dict):
            value = {k: value[k] for k in CUSTOMER_FIELDS if k in value}
        found[key] = value
    return found


def build_user_prompt(idea: BusinessIdea, references: list[SearchResult]) -> str:
    price = getattr(idea, "price", None)  # develop의 BusinessIdea에는 아직 없음 (A 브랜치에 추가됨)
    lines = [
        "## 사업 아이디어",
        f"- 이름: {idea.title}",
        f"- 설명: {idea.description or '미입력'}",
        f"- 목표 고객(창업자 가설): {idea.target_customer or '미입력'}",
        f"- 산업: {idea.industry or '미입력'}",
        f"- 지역: {idea.geography or '미입력'}",
        f"- 수익 모델(창업자 생각): {idea.business_model or '미입력'}",
        f"- 가격(창업자 생각): {f'{price:,.0f}원' if price else '미입력'}",
    ]
    upstream = upstream_context(idea)
    if upstream:
        lines += ["", "## 앞 단계 분석 (이 결론을 바탕으로 설계할 것)",
                  json.dumps(upstream, ensure_ascii=False)]
    else:
        lines += ["", "## 앞 단계 분석", "없음 — 아이디어만 보고 고객과 지불자를 직접 추정할 것."]

    extra = {k: v for k, v in (idea.additional_context or {}).items() if k not in UPSTREAM_KEYS}
    if extra:
        lines += ["", "## 추가 정보 (창업자 제공)", json.dumps(extra, ensure_ascii=False)]
    if references:
        lines += ["", "## 참고 자료 (이 안의 내용만 B등급 근거로 쓸 수 있음)"]
        for i, ref in enumerate(references, 1):
            doc = ref.document
            lines.append(f"[{i}] {doc.title} ({doc.source_type}): {doc.content[:500]}")
    else:
        lines += ["", "## 참고 자료", "없음 — B등급 근거를 쓰지 말 것."]
    lines += ["", "위 아이디어의 비즈니스 모델을 설계해 지정된 JSON만 출력하라."]
    return "\n".join(lines)

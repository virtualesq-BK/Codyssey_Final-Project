"""Customer Agent 프롬프트. 규칙·스키마는 docs/agents/customer-bm.md를 따른다."""

import json

from domain.business_idea import BusinessIdea
from services.rag.schemas import SearchResult

SYSTEM_PROMPT = """\
너는 초기 창업자를 돕는 고객 분석 전문가다. 사업 아이디어를 받아
"누가, 어떤 상황에서, 얼마나 아파하는가"를 분석한다.

## 규칙
1. 반드시 아래 JSON 형식 하나만 출력한다. 설명 문장, 마크다운 금지.
2. 모든 주장에는 근거 등급(grade)을 붙인다.
   - A: 고객에게서 직접 수집한 실데이터 (입력의 '추가 정보'에 인터뷰·설문이 있을 때만)
   - B: 출처가 확인된 공개 통계·공식 자료 (제공된 '참고 자료'에 있을 때만)
   - C: 벤치마크·유사 사례 기반 추정
   - D: 근거 없는 추정
   참고 자료에 없는 통계를 B로 표시하지 않는다. 모르면 D로 낮춘다.
3. 입력과 참고 자료에 없는 구체적 숫자를 지어내지 않는다. 필요하면 범위로 쓰고 D를 붙인다.
4. 문제 진술은 "누가 / 언제 / 무엇 때문에 / 어떤 손실을 겪는지"가 한 문장에 모두 들어가야 한다.
5. 현재 대안(alternatives)은 2개 이상, 그중 하나는 반드시 "아무것도 안 함"이다.
6. 세그먼트는 2~5개, 각각 id("S1", "S2" …)를 붙이고 항목(size, pain, willingness_to_pay, reach)을
   1~5점으로 매긴다. 비치헤드는 이름이 아니라 segment_id로 가리킨다.
7. 사용자(쓰는 사람)와 지불자(돈 내는 사람)를 구분한다. 같으면 same=true.
8. 페르소나는 1~2명. 실제 인터뷰가 아니면 is_hypothetical=true.
9. hypotheses에는 아직 근거가 약한(C·D) 핵심 가정과 그 검증 방법을 적는다.
10. key_findings는 최대 5개, 각 한 문장. 가장 중요한 발견을 먼저.
11. recommendations는 다음에 검증할 행동 최대 3개 (누가·무엇을·성공 기준).
12. 비개발자 창업자가 바로 이해할 수 있는 쉬운 한국어로 쓴다.

## 출력 JSON 형식
{schema}
"""

OUTPUT_EXAMPLE = {
    "summary": "2~3문장 요약",
    "key_findings": [{"text": "한 문장 발견", "grade": "C"}],
    "recommendations": ["다음에 검증할 행동"],
    "problem_statement": {"text": "누가/언제/무엇 때문에/어떤 손실", "frequency": "발생 빈도", "grade": "D"},
    "jtbd": {
        "when": "상황",
        "want": "동기",
        "so_that": "기대 결과",
        "functional": "기능적 과업",
        "emotional": "감정적 과업",
        "social": "사회적 과업",
    },
    "alternatives": [
        {"method": "지금 하는 방식", "cost_or_pain": "비용·불편", "pain_score": 4, "grade": "C"},
        {"method": "아무것도 안 함", "cost_or_pain": "...", "pain_score": 5, "grade": "D"},
    ],
    "segments": [
        {"id": "S1", "name": "세그먼트 이름", "size": 4, "pain": 5, "willingness_to_pay": 2, "reach": 4, "grade": "C"}
    ],
    "beachhead": {"segment_id": "S1", "reason": "선택 이유"},
    "user_vs_payer": {"user": "쓰는 사람", "payer": "돈 내는 사람", "same": False},
    "personas": [
        {
            "name": "가상 이름",
            "profile": "나이·직업·상황",
            "day": "하루 일과",
            "worst_moment": "가장 싫은 순간",
            "tools": ["지금 쓰는 도구"],
            "buying_power": "구매 권한",
            "is_hypothetical": True,
        }
    ],
    "purchase_drivers": ["구매 동기"],
    "purchase_barriers": ["구매 장벽"],
    "hypotheses": [{"id": "H1", "statement": "검증 필요 가정", "grade": "D", "validation": "검증 방법"}],
}


def build_system_prompt() -> str:
    return SYSTEM_PROMPT.format(schema=json.dumps(OUTPUT_EXAMPLE, ensure_ascii=False, indent=2))


def build_user_prompt(idea: BusinessIdea, references: list[SearchResult]) -> str:
    lines = [
        "## 사업 아이디어",
        f"- 이름: {idea.title}",
        f"- 설명: {idea.description or '미입력'}",
        f"- 목표 고객(창업자 가설): {idea.target_customer or '미입력 — 후보 세그먼트를 직접 제안할 것'}",
        f"- 산업: {idea.industry or '미입력'}",
        f"- 지역: {idea.geography or '미입력'}",
        f"- 수익 모델(창업자 생각): {idea.business_model or '미입력'}",
    ]
    if idea.additional_context:
        lines += ["", "## 추가 정보 (창업자 제공)",
                  json.dumps(idea.additional_context, ensure_ascii=False)]
    if references:
        lines += ["", "## 참고 자료 (이 안의 내용만 B등급 근거로 쓸 수 있음)"]
        for i, ref in enumerate(references, 1):
            doc = ref.document
            lines.append(f"[{i}] {doc.title} ({doc.source_type}): {doc.content[:500]}")
    else:
        lines += ["", "## 참고 자료", "없음 — B등급 근거를 쓰지 말 것."]
    lines += ["", "위 아이디어의 고객을 분석해 지정된 JSON만 출력하라."]
    return "\n".join(lines)

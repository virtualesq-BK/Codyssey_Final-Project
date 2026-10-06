"""Business Model Agent 동작 테스트 — 구조·후처리·앞 단계 결과 반영·실패 처리를 검사한다."""

import copy
import json

from agents.business_model import BusinessModelAgent
from domain.agent_result import AgentStatus
from domain.business_idea import BusinessIdea
from services.llm.provider import FakeLLMProvider, LLMProvider

VALID = {
    "summary": "센터 연간 구독이 가장 현실적이다.",
    "key_findings": [{"text": f"발견 {i}", "grade": "C"} for i in range(6)],
    "recommendations": ["센터 5곳 가격 인터뷰"],
    "value_proposition": {"for_whom": "다문화가족지원센터", "problem": "아동별 수준 차", "offer": "교과 어휘 진단·학습"},
    "revenue_model_candidates": [
        {"model": "센터 연간 구독", "fit": 0.85, "rationale": "예산 있음", "grade": "C"},
        {"model": "부모 월 구독", "fit": 0.3, "rationale": "지불 여력 낮음", "grade": "D"},
    ],
    "chosen_model": "센터 연간 구독",
    "payer_type": "B2G",
    "pricing": {
        "price_krw": 1200000, "billing_period": "year", "unit": "center",
        "range_low_krw": 900000, "range_high_krw": 1500000, "rationale": "유사 기관 도구 가격", "grade": "D",
    },
    "price_ladder": [{"plan": "기본", "price_krw": 900000}, {"plan": "확장", "price_krw": 2000000}],
    "channels": [{"channel": "지자체 공모", "role": "구매", "grade": "C"}],
}


class RecordingLLM(LLMProvider):
    name = "recording"

    def __init__(self, response: str) -> None:
        super().__init__()
        self.response, self.user_prompt = response, ""

    async def generate(self, system_prompt, user_prompt, model=None, temperature=0.2) -> str:
        self.user_prompt = user_prompt
        return self.response


async def test_valid_json_succeeds_with_handoff_and_checks(idea):
    result = await BusinessModelAgent(llm=FakeLLMProvider(json.dumps(VALID, ensure_ascii=False))).run(idea)

    assert result.status == AgentStatus.SUCCESS
    meta = result.metadata
    assert meta["handoff_to_financial"] == {
        "price_krw": 1200000, "billing_period": "year", "unit": "center", "payer_type": "B2G",
    }
    assert meta["used_upstream"] == []
    assert len(result.findings) == 5
    # 가격 D(.25) + 후보 C(.5)·D(.25) + 채널 C(.5) + 발견 5개 C(2.5) = 4.0 / 9
    assert result.confidence == 0.44
    assert meta["quality_checks"] == {
        "chosen_model_in_candidates": True,
        "chosen_model_is_best_fit": True,
        "price_within_range": True,
        "price_has_rationale": True,
        "price_ladder_within_range": False,  # 확장 200만 원이 범위 밖
    }


async def test_customer_analysis_is_passed_into_prompt():
    idea = BusinessIdea(
        title="다문화 한국어",
        additional_context={
            "customer_analysis": {
                "beachhead": {"segment": "다문화가족지원센터", "reason": "예산 보유"},
                "user_vs_payer": {"user": "아동", "payer": "센터", "same": False},
                "personas": [{"name": "란 씨"}],  # BM에 불필요한 칸은 빠져야 함
            },
            "interview_notes": "센터 담당자 2명 인터뷰",
        },
    )
    llm = RecordingLLM(json.dumps(VALID, ensure_ascii=False))
    result = await BusinessModelAgent(llm=llm).run(idea)

    assert result.metadata["used_upstream"] == ["customer_analysis"]
    assert "## 앞 단계 분석 (이 결론을 바탕으로 설계할 것)" in llm.user_prompt
    assert "다문화가족지원센터" in llm.user_prompt
    assert "란 씨" not in llm.user_prompt
    assert "센터 담당자 2명 인터뷰" in llm.user_prompt  # 앞 단계가 아닌 추가 정보는 따로 전달


async def test_chosen_model_not_in_candidates_is_flagged(idea):
    data = copy.deepcopy(VALID)
    data["chosen_model"] = "광고 수익"
    result = await BusinessModelAgent(llm=FakeLLMProvider(json.dumps(data))).run(idea)
    assert result.metadata["quality_checks"]["chosen_model_in_candidates"] is False


async def test_invalid_payer_type_is_partial(idea):
    data = copy.deepcopy(VALID)
    data["payer_type"] = "개인"
    result = await BusinessModelAgent(llm=FakeLLMProvider(json.dumps(data))).run(idea)
    assert result.status == AgentStatus.PARTIAL
    assert "payer_type" in result.metadata["validation_errors"]


async def test_non_json_response_is_partial(idea):
    result = await BusinessModelAgent(llm=FakeLLMProvider()).run(idea)
    assert result.status == AgentStatus.PARTIAL
    assert result.metadata["raw_response"] == "fake response"


async def test_missing_llm_is_failed(idea):
    result = await BusinessModelAgent().run(idea)
    assert result.status == AgentStatus.FAILED

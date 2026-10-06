"""Customer Agent 동작 테스트 — LLM 문장은 검사하지 않고 구조·후처리·실패 처리를 검사한다."""

import copy
import json

from agents.customer import CustomerAgent
from domain.agent_result import AgentStatus
from services.llm.provider import FakeLLMProvider, LLMProvider
from services.rag.rag_service import RAGService
from services.rag.schemas import Document

VALID = {
    "summary": "쓰는 사람과 돈 내는 사람이 다르다.",
    "key_findings": [{"text": f"발견 {i}", "grade": "C"} for i in range(7)],
    "recommendations": ["교사 8명 실측", "교감 5명 인터뷰", "보안 담당 3명 확인", "네 번째"],
    "problem_statement": {"text": "교사가 학기말에 자료를 모으느라 하루를 쓴다", "frequency": "학기당 2회", "grade": "B"},
    "jtbd": {"when": "학기말", "want": "기록이 양식이 되길", "so_that": "야근 없이 제출"},
    "alternatives": [
        {"method": "엑셀 여러 개", "cost_or_pain": "인계 시 유실", "pain_score": 4, "grade": "C"},
        {"method": "아무것도 안 함", "cost_or_pain": "몰아서 작성", "pain_score": 5, "grade": "D"},
    ],
    "segments": [
        {"id": "S1", "name": "겸임 교사", "size": 4, "pain": 5, "willingness_to_pay": 2, "reach": 4, "total": 99, "grade": "C"},
        {"id": "S2", "name": "교감", "size": 4, "pain": 2, "willingness_to_pay": 5, "reach": 2, "grade": "C"},
    ],
    "beachhead": {"segment_id": "S1", "reason": "고통이 가장 큼"},
    "user_vs_payer": {"user": "교사", "payer": "교감·행정실", "same": False},
    "personas": [{"name": "김교사", "profile": "초등 5년차", "is_hypothetical": False}],
    "hypotheses": [{"id": "H1", "statement": "1회 4시간 이상", "grade": "D", "validation": "실측"}],
}


class RecordingLLM(LLMProvider):
    name = "recording"

    def __init__(self, response: str = "", error: Exception | None = None) -> None:
        super().__init__()
        self.response, self.error, self.user_prompt = response, error, ""

    async def generate(self, system_prompt, user_prompt, model=None, temperature=0.2) -> str:
        self.user_prompt = user_prompt
        if self.error:
            raise self.error
        return self.response


async def test_valid_json_succeeds_with_code_postprocessing(idea):
    result = await CustomerAgent(llm=FakeLLMProvider(json.dumps(VALID, ensure_ascii=False))).run(idea)

    assert result.status == AgentStatus.SUCCESS
    meta = result.metadata
    assert meta["schema_version"] == "c-0.2"
    assert meta["segments"][0]["total"] == 15  # LLM이 준 99가 아니라 코드 계산값
    assert meta["personas"][0]["is_hypothetical"] is True  # 인터뷰 자료 없음 → 가상 강제
    assert len(result.findings) == 5 and result.findings[0] == "발견 0 [C]"
    assert len(result.recommendations) == 3
    # 문제 B(.75) + 대안 C(.5)·D(.25) + 세그먼트 C·C(1.0) + 발견 5개 C(2.5) = 5.0 / 10
    assert result.confidence == 0.5
    assert meta["quality_checks"] == {
        "has_user_vs_payer": True,
        "has_do_nothing_alternative": True,
        "beachhead_is_top_segment": True,
        "beachhead_has_reason": True,
        "has_hypotheses": True,
    }


async def test_json_inside_code_fence_is_extracted(idea):
    raw = "분석 결과입니다.\n```json\n" + json.dumps(VALID, ensure_ascii=False) + "\n```"
    result = await CustomerAgent(llm=FakeLLMProvider(raw)).run(idea)
    assert result.status == AgentStatus.SUCCESS


async def test_non_json_response_is_partial(idea):
    result = await CustomerAgent(llm=FakeLLMProvider()).run(idea)  # "fake response"
    assert result.status == AgentStatus.PARTIAL
    assert result.confidence == 0.0
    assert result.summary.startswith("INSUFFICIENT_EVIDENCE")
    assert result.metadata["raw_response"] == "fake response"


async def test_missing_required_field_is_partial(idea):
    broken = copy.deepcopy(VALID)
    broken["alternatives"] = broken["alternatives"][:1]  # 2개 이상 필수
    result = await CustomerAgent(llm=FakeLLMProvider(json.dumps(broken))).run(idea)
    assert result.status == AgentStatus.PARTIAL
    assert "alternatives" in result.metadata["validation_errors"]


async def test_beachhead_pointing_to_unknown_segment_is_partial(idea):
    broken = copy.deepcopy(VALID)
    broken["beachhead"]["segment_id"] = "S9"
    result = await CustomerAgent(llm=FakeLLMProvider(json.dumps(broken))).run(idea)
    assert result.status == AgentStatus.PARTIAL


async def test_duplicate_segment_ids_are_partial(idea):
    broken = copy.deepcopy(VALID)
    broken["segments"][1]["id"] = "S1"
    result = await CustomerAgent(llm=FakeLLMProvider(json.dumps(broken))).run(idea)
    assert result.status == AgentStatus.PARTIAL


async def test_llm_error_is_failed(idea):
    result = await CustomerAgent(llm=RecordingLLM(error=RuntimeError("timeout"))).run(idea)
    assert result.status == AgentStatus.FAILED
    assert result.metadata["error_type"] == "RuntimeError"


async def test_missing_llm_is_failed(idea):
    result = await CustomerAgent().run(idea)
    assert result.status == AgentStatus.FAILED
    assert result.metadata["error_type"] == "MissingLLMProvider"


async def test_rag_results_become_evidence_and_prompt_references(idea):
    rag = RAGService()
    await rag.add_document(Document(id="d1", title="소상공인 실태조사", content="소상공인 장부 작성 실태", source_type="public_stat"))
    llm = RecordingLLM(response=json.dumps(VALID, ensure_ascii=False))

    result = await CustomerAgent(llm=llm, rag=rag).run(idea)

    assert result.evidence and result.evidence[0].source_title == "소상공인 실태조사"
    assert "[1] 소상공인 실태조사" in llm.user_prompt

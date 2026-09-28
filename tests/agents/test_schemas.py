"""스키마 계약 테스트."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from domain.agent_result import AgentResult, AgentStatus, Evidence
from domain.business_idea import BusinessIdea
from domain.decision_result import DecisionResult


def test_confidence_range_enforced():
    with pytest.raises(ValidationError):
        AgentResult(agent_name="x", status=AgentStatus.SUCCESS, confidence=1.5)


def test_evidence_structure():
    e = Evidence(source_title="t", source_type="report", claim="c", relevance=0.5)
    assert e.url is None and e.published_at is None


def test_evidence_legal_fields_optional():
    """Legal 전용 필드는 선택이며 다른 Agent는 채우지 않아도 됩니다."""
    e = Evidence(source_title="t", source_type="statute", claim="c")
    assert e.source_level is None
    assert e.citation is None
    assert e.retrieved_at is None


def test_evidence_legal_fields_accepted():
    e = Evidence(
        source_title="공정거래법",
        source_type="statute",
        claim="시장지배적 사업자 금지",
        source_level="statute",
        citation="공정거래법 제3조 제1항",
        retrieved_at=datetime(2026, 1, 1, 12, 0),
    )
    assert e.citation == "공정거래법 제3조 제1항"


def test_decision_result_has_legal_field():
    d = DecisionResult()
    assert hasattr(d, "legal_compliance_assessment")
    assert d.legal_compliance_assessment == ""


def test_business_idea_new_fields():
    idea = BusinessIdea(title="테스트", price=9900, country="KR")
    assert idea.price == 9900
    assert idea.country == "KR"
    assert idea.geography == ""  # 기존 필드 호환 확인

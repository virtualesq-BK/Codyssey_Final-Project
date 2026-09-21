import pytest
from pydantic import ValidationError

from domain.agent_result import AgentResult, AgentStatus, Evidence


def test_confidence_range_enforced():
    with pytest.raises(ValidationError):
        AgentResult(agent_name="x", status=AgentStatus.SUCCESS, confidence=1.5)


def test_evidence_structure():
    e = Evidence(source_title="t", source_type="report", claim="c", relevance=0.5)
    assert e.url is None and e.published_at is None

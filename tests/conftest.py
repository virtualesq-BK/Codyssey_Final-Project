import pytest

from domain.business_idea import BusinessIdea


@pytest.fixture
def idea() -> BusinessIdea:
    return BusinessIdea(
        title="AI 회계 도우미",
        description="소상공인용 자동 장부",
        target_customer="소상공인",
        industry="fintech",
        geography="KR",
        business_model="SaaS",
    )

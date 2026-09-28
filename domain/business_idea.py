from typing import Any

from pydantic import BaseModel, Field


class BusinessIdea(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    target_customer: str = ""
    industry: str = ""
    geography: str = ""          # 기존 필드 유지 (팀원 코드 호환)
    country: str = ""            # API /api/analyze의 country 파라미터에 매핑
    business_model: str = ""
    price: float | None = None   # 예상 가격 (선택)
    additional_context: dict[str, Any] = Field(default_factory=dict)

from typing import Any

from pydantic import BaseModel, Field


class BusinessIdea(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    target_customer: str = ""
    industry: str = ""
    geography: str = ""
    business_model: str = ""
    additional_context: dict[str, Any] = Field(default_factory=dict)

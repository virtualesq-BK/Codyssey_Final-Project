"""API 요청·응답 스키마 (도메인 스키마와 분리)."""

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """POST /api/analyze 요청 바디."""

    business_idea: str = Field(min_length=1, description="사업 아이디어 설명")
    target_customer: str = ""
    target_market: str = ""
    country: str = ""
    price: float | None = None
    additional_context: dict[str, Any] = Field(default_factory=dict)


class AnalysisStatusResponse(BaseModel):
    """분석 작업 수락 응답."""

    analysis_id: str
    status: str = "accepted"
    message: str = "분석이 시작되었습니다."


class AnalysisResultResponse(BaseModel):
    """GET /api/analysis/{analysis_id} 응답."""

    analysis_id: str
    status: str  # "processing" | "completed" | "failed"
    result: dict[str, Any] | None = None
    error: str | None = None

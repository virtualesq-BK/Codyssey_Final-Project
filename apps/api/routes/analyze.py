"""POST /api/analyze — 사업 아이디어 분석 요청."""

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException

from agents.business_model import BusinessModelAgent
from agents.competitor import CompetitorAgent
from agents.customer import CustomerAgent
from agents.decision.agent import DecisionAgent
from agents.financial import FinancialAgent
from agents.legal_compliance import LegalComplianceAgent
from agents.market import MarketAgent
from agents.orchestrator.agent import OrchestratorAgent
from agents.risk import RiskAgent
from apps.api.schemas import AnalysisResultResponse, AnalysisStatusResponse, AnalyzeRequest
from domain.business_idea import BusinessIdea

router = APIRouter(prefix="/api")

# ------------------------------------------------------------------ #
# In-memory store (TODO: DB 구현 후 repository 로 교체 — D 담당)      #
# ------------------------------------------------------------------ #
_results: dict[str, AnalysisResultResponse] = {}


def _make_orchestrator() -> OrchestratorAgent:
    """기본 Agent 구성. 실제 LLM/RAG 주입은 DI 컨테이너로 교체 예정."""
    agents = [
        MarketAgent(),
        CompetitorAgent(),
        CustomerAgent(),
        BusinessModelAgent(),
        FinancialAgent(),
        RiskAgent(),
        LegalComplianceAgent(),
    ]
    return OrchestratorAgent(agents=agents, decision=DecisionAgent())


async def _run_analysis(analysis_id: str, idea: BusinessIdea) -> None:
    """백그라운드 분석 태스크."""
    try:
        orch = _make_orchestrator()
        _, decision = await orch.analyze(idea)
        _results[analysis_id] = AnalysisResultResponse(
            analysis_id=analysis_id,
            status="completed",
            result=decision.model_dump(),
        )
    except Exception as exc:  # noqa: BLE001
        _results[analysis_id] = AnalysisResultResponse(
            analysis_id=analysis_id,
            status="failed",
            error=str(exc),
        )


@router.post("/analyze", response_model=AnalysisStatusResponse, status_code=202)
async def analyze(body: AnalyzeRequest, background_tasks: BackgroundTasks) -> AnalysisStatusResponse:
    """
    사업 아이디어 분석을 시작합니다.

    분석은 백그라운드에서 실행되며, 반환된 analysis_id 로
    GET /api/analysis/{analysis_id} 에서 결과를 조회합니다.
    """
    analysis_id = str(uuid.uuid4())
    idea = BusinessIdea(
        title=body.business_idea[:200],
        description=body.business_idea,
        target_customer=body.target_customer,
        geography=body.target_market,
        country=body.country,
        price=body.price,
        additional_context=body.additional_context,
    )
    _results[analysis_id] = AnalysisResultResponse(
        analysis_id=analysis_id, status="processing"
    )
    background_tasks.add_task(_run_analysis, analysis_id, idea)
    return AnalysisStatusResponse(analysis_id=analysis_id)


@router.get("/analysis/{analysis_id}", response_model=AnalysisResultResponse)
async def get_analysis(analysis_id: str) -> AnalysisResultResponse:
    """분석 결과를 조회합니다."""
    entry = _results.get(analysis_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="analysis_id 를 찾을 수 없습니다.")
    return entry

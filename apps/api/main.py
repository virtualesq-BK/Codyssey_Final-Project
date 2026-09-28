from fastapi import FastAPI

from apps.api.routes.analyze import router as analyze_router
from apps.api.routes.health import router as health_router

app = FastAPI(
    title="AI Business Decision Copilot",
    description="Multi-Agent 기반 사업 의사결정 지원 시스템",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(analyze_router)

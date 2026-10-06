"""C 담당 에이전트를 기획서 원안 순서(고객 → BM)로 실제 LLM에 이어 돌린다.

오케스트레이터가 단계별 실행을 지원하기 전까지 연결 결과를 미리 확인하는 용도.
고객 분석 metadata를 BusinessIdea.additional_context["customer_analysis"]로 BM에 넘긴다.

사용:
    .venv/bin/python scripts/run_c_pipeline.py              # 기본 예시(다문화 한국어 SaaS)
    .venv/bin/python scripts/run_c_pipeline.py idea.json    # BusinessIdea 형식 JSON 파일
결과: runs/c-pipeline-<시각>.json  (runs/는 깃에 올리지 않는다)
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from agents.business_model import BusinessModelAgent
from agents.customer import CustomerAgent
from domain.agent_result import AgentResult, AgentStatus
from domain.business_idea import BusinessIdea
from services.llm.factory import create_provider

KST = ZoneInfo("Asia/Seoul")

SAMPLE_IDEA = BusinessIdea(
    title="다문화 아동 한국어 학습 SaaS",
    description=(
        "다문화 가정 아이들이 학교 수업을 따라갈 수 있도록 돕는 한국어 학습 서비스. "
        "아이의 한국어 수준을 진단하고 교과 어휘 중심으로 맞춤 학습을 제공한다."
    ),
    industry="에듀테크",
    geography="KR",
    business_model="SaaS 구독",
)


def show(title: str, result: AgentResult) -> None:
    print(f"\n=== {title}: {result.status.value} / 신뢰도 {result.confidence}")
    print(result.summary)
    for f in result.findings:
        print(f" - {f}")


async def main() -> None:
    idea = (
        BusinessIdea.model_validate_json(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if len(sys.argv) > 1
        else SAMPLE_IDEA
    )
    llm = create_provider()
    print(f"실행 중… ({idea.title}) — 고객 → BM 순서, 2~3분 걸릴 수 있어요")

    customer = await CustomerAgent(llm=llm).run(idea)
    show("고객 에이전트", customer)

    bm_input = idea
    if customer.status == AgentStatus.SUCCESS:
        bm_input = idea.model_copy(update={"additional_context": {
            **idea.additional_context, "customer_analysis": customer.metadata,
        }})
    bm = await BusinessModelAgent(llm=llm).run(bm_input)
    show("BM 에이전트", bm)
    if bm.status == AgentStatus.SUCCESS:
        print("\nD(재무)에게 넘길 값:", bm.metadata["handoff_to_financial"])
        print("품질 검사:", bm.metadata["quality_checks"])

    usage = [u.model_dump(mode="json") for u in llm.tracker.records]
    total = sum(u["estimated_cost"] or 0 for u in usage)
    print(f"\n호출 {len(usage)}회 · 출력 {sum(u['output_tokens'] or 0 for u in usage)} 토큰"
          f" · 추정 ${total:.4f}")

    out_dir = Path("runs")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"c-pipeline-{datetime.now(KST):%Y%m%d-%H%M%S}.json"
    out.write_text(json.dumps({
        "idea": idea.model_dump(),
        "customer": customer.model_dump(mode="json"),
        "business_model": bm.model_dump(mode="json"),
        "usage": usage,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"저장: {out}")


if __name__ == "__main__":
    asyncio.run(main())

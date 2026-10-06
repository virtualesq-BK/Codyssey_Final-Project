"""Customer Agent를 실제 LLM으로 한 번 실행하고 결과를 JSON으로 저장한다.

사용:
    .venv/bin/python scripts/run_customer_agent.py                 # 기본 예시(다문화 한국어 SaaS)
    .venv/bin/python scripts/run_customer_agent.py idea.json       # BusinessIdea 형식 JSON 파일
결과: runs/customer-<시각>.json  (runs/는 깃에 올리지 않는다)
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from agents.customer import CustomerAgent
from domain.business_idea import BusinessIdea
from services.llm.factory import create_provider

KST = ZoneInfo("Asia/Seoul")

SAMPLE_IDEA = BusinessIdea(
    title="다문화 아동 한국어 학습 SaaS",
    description=(
        "다문화 가정 아이들이 학교 수업을 따라갈 수 있도록 돕는 한국어 학습 서비스. "
        "아이의 한국어 수준을 진단하고 교과 어휘 중심으로 맞춤 학습을 제공한다."
    ),
    target_customer="",
    industry="에듀테크",
    geography="KR",
    business_model="SaaS 구독",
)


async def main() -> None:
    idea = (
        BusinessIdea.model_validate_json(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if len(sys.argv) > 1
        else SAMPLE_IDEA
    )
    llm = create_provider()
    print(f"실행 중… ({idea.title}) — 1~2분 걸릴 수 있어요")
    result = await CustomerAgent(llm=llm).run(idea)

    out_dir = Path("runs")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"customer-{datetime.now(KST):%Y%m%d-%H%M%S}.json"
    usage = [u.model_dump(mode="json") for u in llm.tracker.records]
    out.write_text(
        json.dumps(
            {"idea": idea.model_dump(), "result": result.model_dump(mode="json"), "usage": usage},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\n상태: {result.status.value} / 신뢰도: {result.confidence}")
    print(f"요약: {result.summary}")
    for f in result.findings:
        print(f" - {f}")
    for u in usage:
        print(f"\n모델 {u['model']} · 입력 {u['input_tokens']} · 출력 {u['output_tokens']} 토큰"
              f" · {u['latency_ms'] / 1000:.1f}초 · 추정 ${u['estimated_cost']}")
    print(f"저장: {out}")


if __name__ == "__main__":
    asyncio.run(main())

# Agent Interface

```python
class BaseAgent:
    name: str
    async def run(self, input_data: BusinessIdea) -> AgentResult: ...
```

- 반환값은 항상 `AgentResult` (`agent_name, status, summary, findings, evidence, recommendations, confidence, metadata`).
- `confidence`는 0.0~1.0. 근거가 없으면 Evidence를 만들어내지 않습니다.
- 스켈레톤 Agent는 `status=not_implemented`를 반환합니다.
- 파이프라인: Document -> Evidence -> Finding -> Recommendation.

# Architecture

```
apps/api (FastAPI) -> agents/orchestrator -> agents/{market,competitor,customer,business_model,financial,risk}
                                          -> agents/decision -> DecisionResult
agents -> services/{llm,rag,search,memory,calculation}
all layers -> domain (BusinessIdea, AgentResult, DecisionResult)
```

- `OrchestratorAgent`는 주입받은 Agent들을 병렬 실행하고, 실패한 Agent는 `FAILED` 결과로 바꿔 워크플로를 계속합니다.
- Agent는 서로를 import하지 않고 `AgentResult`로만 데이터를 주고받습니다.

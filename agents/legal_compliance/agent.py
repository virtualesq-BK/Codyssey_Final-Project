"""
Legal & Compliance Agent

포지셔닝:
    사업 의사결정 과정에서 확인해야 할 법률·규제 리스크와 관련 근거를
    탐색·정리하는 AI Agent입니다.

    ⚠️ 이 Agent는 확정적인 법률 자문을 제공하는 AI 변호사가 아닙니다.
    법적 판단 확정, 법적 승소 가능성 보장, 법률 자문을 대체하지 않습니다.
    최종 법률 판단은 반드시 전문 법률가에게 문의하십시오.
"""

from agents.base.agent import BaseAgent
from domain.agent_result import AgentResult
from domain.business_idea import BusinessIdea
from services.llm.provider import LLMProvider
from services.rag.rag_service import RAGService


class LegalComplianceAgent(BaseAgent):
    """
    법률·규제 관련 리스크를 탐색하고 근거를 정리합니다.

    RAG 검색 필터 예시::

        query:   "사업자 등록 허가 규제 의무"
        filters: {"source_type": "official", "country": <country>}

    Evidence에는 source_level, citation, retrieved_at을 포함할 수 있습니다.
    근거가 불충분할 경우 finding에 "INSUFFICIENT_EVIDENCE"를 기록합니다.
    """

    name = "legal_compliance"

    def __init__(self, llm: LLMProvider | None = None, rag: RAGService | None = None) -> None:
        self.llm = llm
        self.rag = rag

    async def run(self, input_data: BusinessIdea) -> AgentResult:
        # TODO (E 담당자):
        #   1. self.rag.search(query, filters={"source_type": "official", "country": ...})
        #   2. Document → Evidence (source_level, citation, retrieved_at 포함)
        #   3. Evidence → Finding → Recommendation
        #   4. 근거 부족 시 finding = "INSUFFICIENT_EVIDENCE" 또는 "추가 검증 필요"
        return self.not_implemented_result()

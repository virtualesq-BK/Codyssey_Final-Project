"""LLM 텍스트 응답에서 JSON 객체를 꺼낸다.

TODO(C): BM Agent도 같은 함수가 필요하다. Agent끼리 import하지 않는 규칙 때문에
services/ 쪽 공통 유틸로 옮기는 것을 Issue로 제안할 예정.
"""

import json
import re
from typing import Any

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json_object(text: str) -> dict[str, Any] | None:
    """코드펜스나 앞뒤 설명이 섞인 응답에서도 첫 JSON 객체를 찾는다. 실패하면 None."""
    if not text:
        return None
    candidates = [m.group(1) for m in _FENCE.finditer(text)]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            value = json.loads(candidate.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return None

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    id: str
    title: str
    content: str
    source_type: str = "unknown"
    url: str | None = None
    published_at: date | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    document: Document
    score: float = 0.0

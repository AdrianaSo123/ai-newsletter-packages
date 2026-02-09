from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class InvestmentIntelItem(BaseModel):
    source: str
    source_record_type: str | None = None
    source_record_id: str | None = None
    url: str | None = None
    title: str | None = None
    summary: str | None = None
    published_at: datetime | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    entities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    raw: dict[str, Any] | None = None

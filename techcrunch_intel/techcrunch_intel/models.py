from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Article:
    title: str
    url: str
    published_at: datetime | None
    summary: str | None = None
    author: str | None = None
    categories: list[str] = field(default_factory=list)
    guid: str | None = None
    source: str = "techcrunch"


@dataclass(frozen=True)
class InvestmentSignal:
    ai_relevant: bool
    company: str | None = None
    amount_text: str | None = None
    stage: str | None = None
    investors: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass(frozen=True)
class IntelRecord:
    article: Article
    investment: InvestmentSignal
    extracted_at: datetime
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # dataclasses -> JSON-friendly
        if self.article.published_at is not None:
            d["article"]["published_at"] = self.article.published_at.isoformat()
        d["extracted_at"] = self.extracted_at.isoformat()
        return d

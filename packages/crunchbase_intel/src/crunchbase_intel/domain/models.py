from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExtractionMethod(str, Enum):
    public_html = "public_html"
    fixture_html = "fixture_html"


class UnavailableField(BaseModel):
    field: str
    reason: str


class ExtractionProvenance(BaseModel):
    source: str = "crunchbase"
    method: ExtractionMethod
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    url: str | None = None


class Investor(BaseModel):
    name: str
    url: str | None = None


class FundingRound(BaseModel):
    round_type: str | None = None
    announced_on: str | None = None
    money_raised: str | None = None
    investors: list[Investor] = Field(default_factory=list)


class Company(BaseModel):
    name: str | None = None
    crunchbase_url: str | None = None
    description: str | None = None
    categories: list[str] = Field(default_factory=list)

    funding_rounds: list[FundingRound] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    company: Company
    provenance: ExtractionProvenance
    unavailable: list[UnavailableField] = Field(default_factory=list)
    raw: dict[str, Any] | None = None

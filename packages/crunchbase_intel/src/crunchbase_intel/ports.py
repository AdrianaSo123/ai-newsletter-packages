from __future__ import annotations

from typing import Protocol

from .domain.models import Company, UnavailableField


class HttpTextFetcher(Protocol):
    def get_text(self, url: str) -> str:
        """Fetch the textual contents of a URL."""


class CompanyPageParser(Protocol):
    def parse_company(self, html: str, *, url: str | None) -> tuple[Company, list[UnavailableField], dict]:
        """Parse HTML into a Company plus unavailable fields and raw parse artifacts."""

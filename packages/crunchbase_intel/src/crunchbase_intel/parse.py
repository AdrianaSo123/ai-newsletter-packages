"""Parsing facade.

The canonical implementation lives in `crunchbase_intel.infrastructure.bs4_parser`.
"""

from typing import Any

from .domain.models import Company, UnavailableField
from .infrastructure.bs4_parser import PublicOrgPageParser


def parse_company_from_html(
    html: str, *, url: str | None = None
) -> tuple[Company, list[UnavailableField], dict[str, Any]]:
    parser = PublicOrgPageParser()
    company, unavailable, raw = parser.parse_company(html, url=url)
    return company, unavailable, raw

from __future__ import annotations

from pathlib import Path

from .application.use_cases import ExtractOrganization
from .domain.models import ExtractionResult
from .infrastructure.bs4_parser import PublicOrgPageParser
from .infrastructure.http_fetcher import PoliteHttpFetcher


class CrunchbaseExtractor:
    """Conservative Crunchbase extractor (public HTML only).

    Design goals:
    - Never fabricate unavailable data
    - Always include provenance
    - Fail explicitly on network/access issues
    """

    def __init__(
        self,
        *,
        min_delay_s: float = 1.0,
        user_agent: str = "crunchbase-intel/0.1.0 (academic; minimal)",
    ) -> None:
        self._min_delay_s = min_delay_s
        self._user_agent = user_agent

    def extract_org_from_url(self, url: str) -> ExtractionResult:
        with PoliteHttpFetcher(user_agent=self._user_agent, min_delay_s=self._min_delay_s) as fetcher:
            use_case = ExtractOrganization(fetcher=fetcher, parser=PublicOrgPageParser())
            return use_case.from_url(url)

    def extract_org_from_html_file(self, path: Path, *, url: str | None = None) -> ExtractionResult:
        # No fetcher needed for local HTML.
        use_case = ExtractOrganization(fetcher=_NoopFetcher(), parser=PublicOrgPageParser())
        return use_case.from_html_file(path, url=url)


class _NoopFetcher:
    def get_text(self, url: str) -> str:  # pragma: no cover
        raise RuntimeError("Noop fetcher: this path should not fetch URLs")

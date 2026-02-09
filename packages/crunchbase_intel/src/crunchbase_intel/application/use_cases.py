from __future__ import annotations

from pathlib import Path

from ..domain.url_policy import validate_org_url
from ..domain.models import ExtractionMethod, ExtractionProvenance, ExtractionResult
from ..ports import CompanyPageParser, HttpTextFetcher


class ExtractOrganization:
    """Application use-case: extract a Company record from Crunchbase inputs."""

    def __init__(self, *, fetcher: HttpTextFetcher, parser: CompanyPageParser) -> None:
        self._fetcher = fetcher
        self._parser = parser

    def from_url(self, url: str) -> ExtractionResult:
        validate_org_url(url)
        html = self._fetcher.get_text(url)
        company, unavailable, raw = self._parser.parse_company(html, url=url)
        prov = ExtractionProvenance(method=ExtractionMethod.public_html, url=url)
        return ExtractionResult(company=company, provenance=prov, unavailable=unavailable, raw=raw)

    def from_html_file(self, path: Path, *, url: str | None = None) -> ExtractionResult:
        html = path.read_text(encoding="utf-8")
        company, unavailable, raw = self._parser.parse_company(html, url=url)
        prov = ExtractionProvenance(method=ExtractionMethod.fixture_html, url=url)
        return ExtractionResult(company=company, provenance=prov, unavailable=unavailable, raw=raw)

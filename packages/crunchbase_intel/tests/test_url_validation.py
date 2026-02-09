from __future__ import annotations

from crunchbase_intel.application.use_cases import ExtractOrganization
from crunchbase_intel.domain.errors import InvalidInputError
from crunchbase_intel.infrastructure.bs4_parser import PublicOrgPageParser


class _NoFetch:
    def get_text(self, url: str) -> str:  # pragma: no cover
        raise AssertionError("Fetcher should not be called for invalid URLs")


def test_rejects_non_org_urls_before_fetch() -> None:
    uc = ExtractOrganization(fetcher=_NoFetch(), parser=PublicOrgPageParser())

    bad = "https://news.crunchbase.com/sections/ai/"
    try:
        uc.from_url(bad)
        assert False, "Expected InvalidInputError"
    except InvalidInputError:
        pass

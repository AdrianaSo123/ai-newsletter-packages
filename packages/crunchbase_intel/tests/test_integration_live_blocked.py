from __future__ import annotations

import os

import pytest

from crunchbase_intel.application.use_cases import ExtractOrganization
from crunchbase_intel.domain.errors import FetchError
from crunchbase_intel.infrastructure.bs4_parser import PublicOrgPageParser
from crunchbase_intel.infrastructure.http_fetcher import PoliteHttpFetcher


@pytest.mark.integration
def test_live_org_url_is_explicit_when_blocked() -> None:
    """Optional integration test.

    Goal: confirm that when Crunchbase blocks public automation (common), we surface a
    structured FetchError (kind/url/status_code) rather than returning partial/misleading output.

    This test is *skipped* unless CRUNCHBASE_INTEL_INTEGRATION=1.
    """

    if (os.getenv("CRUNCHBASE_INTEL_INTEGRATION") or "").strip() != "1":
        pytest.skip("Set CRUNCHBASE_INTEL_INTEGRATION=1 to enable live integration tests")

    url = "https://www.crunchbase.com/organization/anthropic"

    with PoliteHttpFetcher(min_delay_s=1.0) as fetcher:
        uc = ExtractOrganization(fetcher=fetcher, parser=PublicOrgPageParser())
        try:
            _ = uc.from_url(url)
        except FetchError as exc:
            # Expected in many environments.
            assert exc.url == url
            assert exc.kind in {"access_denied", "rate_limited", "http_error", "network_error"}
            if exc.kind == "access_denied":
                assert exc.status_code in {401, 403}
            return

    # If we got here, Crunchbase allowed access from this environment.
    # Avoid making brittle claims about public accessibility.
    pytest.skip("Crunchbase org page was accessible; cannot assert blocked behavior")

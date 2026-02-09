from __future__ import annotations

import os
from pathlib import Path

import pytest

from crunchbase_intel.extractor import CrunchbaseExtractor


def test_user_provided_snapshot_extracts_company_name() -> None:
    """Optional test: validates extraction against a real, user-provided snapshot.

    This test is skipped by default to keep CI stable and to avoid committing
    Crunchbase HTML into the repo.
    """

    snapshot = (os.getenv("CRUNCHBASE_INTEL_SNAPSHOT_HTML") or "").strip()
    if not snapshot:
        pytest.skip("CRUNCHBASE_INTEL_SNAPSHOT_HTML not set")

    path = Path(snapshot)
    if not path.exists():
        pytest.skip(f"Snapshot not found: {path}")

    res = CrunchbaseExtractor().extract_org_from_html_file(path)

    # Minimal correctness claim: we can parse a non-empty company name from the snapshot.
    assert res.company.name is not None
    assert res.company.name.strip()

    # Provenance must always be explicit.
    assert res.provenance.source == "crunchbase"
    assert res.provenance.method.value == "fixture_html"

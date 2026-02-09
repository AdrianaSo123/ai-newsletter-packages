from __future__ import annotations

from pathlib import Path

from crunchbase_intel.extractor import CrunchbaseExtractor


def test_fixture_extract_provenance_and_unavailable() -> None:
    extractor = CrunchbaseExtractor()
    fixture = Path(__file__).parent / "fixtures" / "org_minimal_jsonld.html"
    res = extractor.extract_org_from_html_file(fixture, url="https://www.crunchbase.com/organization/crunchbase")

    assert res.provenance.source == "crunchbase"
    assert res.provenance.method.value == "fixture_html"
    assert res.company.crunchbase_url is not None

    # We do not fabricate funding rounds/investors from this minimal input.
    assert res.company.funding_rounds == []

    unavailable_fields = {u.field for u in res.unavailable}
    assert "funding_rounds" in unavailable_fields
    assert "investors" in unavailable_fields
    assert "people_roles" in unavailable_fields


def test_blank_html_does_not_fabricate_name() -> None:
    extractor = CrunchbaseExtractor()
    fixture = Path(__file__).parent / "fixtures" / "blank.html"
    res = extractor.extract_org_from_html_file(fixture)

    assert res.company.name is None
    unavailable_fields = {u.field for u in res.unavailable}
    assert "company.name" in unavailable_fields

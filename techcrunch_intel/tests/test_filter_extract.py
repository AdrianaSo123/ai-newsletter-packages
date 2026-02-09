from __future__ import annotations

from datetime import datetime, timezone

from techcrunch_intel.filter import is_ai_related, is_investment_related, is_relevant
from techcrunch_intel.extract import extract_investment_signal
from techcrunch_intel.kg import build_kg_bundle
from techcrunch_intel.models import Article
from techcrunch_intel.keywords import is_ai_related_text


def test_filter_relevance_basic() -> None:
    a = Article(
        title="Acme AI raises $25M in Series A",
        url="https://example.com",
        published_at=datetime.now(timezone.utc),
        summary="The generative AI startup announced funding led by Sequoia.",
        categories=["AI"],
    )
    assert is_ai_related(a)
    assert is_investment_related(a)
    assert is_relevant(a)


def test_ai_keyword_token_boundary() -> None:
    assert is_ai_related_text("We build AI models") is True
    assert is_ai_related_text("We were laid off yesterday") is False


def test_extract_ai_relevant_includes_categories() -> None:
    # Title/summary don't mention AI, but category does.
    a = Article(
        title="Acme raises $10M in Series A",
        url="https://example.com/2",
        published_at=None,
        summary="Funding led by Example Ventures.",
        categories=["AI"],
    )
    sig = extract_investment_signal(a)
    assert sig.ai_relevant is True


def test_extract_amount_stage_company() -> None:
    a = Article(
        title="Acme AI raises $25M in Series A",
        url="https://example.com",
        published_at=None,
        summary=None,
    )
    sig = extract_investment_signal(a)
    assert sig.company == "Acme AI"
    assert sig.amount_text == "$25M"
    assert sig.stage == "series a"


def test_kg_bundle_contains_required_relationship_types() -> None:
    a = Article(
        title="Acme AI raises $25M in Series A",
        url="https://example.com/1",
        published_at=datetime.now(timezone.utc),
        summary="Funding led by Sequoia.",
    )
    sig = extract_investment_signal(a)
    # Inject an investor to ensure the edge exists.
    sig2 = type(sig)(
        ai_relevant=sig.ai_relevant,
        company=sig.company,
        amount_text=sig.amount_text,
        stage=sig.stage,
        investors=["Sequoia Capital"],
        notes=sig.notes,
    )

    from techcrunch_intel.models import IntelRecord

    r = IntelRecord(article=a, investment=sig2, extracted_at=datetime.now(timezone.utc), raw=None)
    bundle = build_kg_bundle([r])
    rel_types = {e["relationship_type"] for e in bundle["relationships"]}
    assert "mentioned_in" in rel_types
    assert "received_investment_from" in rel_types
    assert "reported_by" in rel_types

from __future__ import annotations

from pathlib import Path

from techcrunch_extractor.fetcher import fetch_rss_items
from techcrunch_extractor.normalizer import normalize_rss_item


class _DummyClient:
    def __init__(self, xml_text: str):
        self._xml_text = xml_text

    def get_text(self, url: str) -> str:  # matches TechCrunchClient.get_text
        return self._xml_text


def test_fetch_rss_items_parses_fixture() -> None:
    xml_text = Path(__file__).parent / "fixtures" / "sample_rss.xml"
    client = _DummyClient(xml_text.read_text(encoding="utf-8"))

    items = fetch_rss_items(client, rss_url="https://example.invalid/feed", limit=10)

    assert len(items) == 1
    assert items[0].guid == "tc-fixture-guid-1"
    assert items[0].title == "Example startup raises $OPENAI"
    assert items[0].link == "https://techcrunch.com/2026/02/01/example/"
    assert "Funding" in items[0].categories


def test_normalize_rss_item_emits_model() -> None:
    xml_text = Path(__file__).parent / "fixtures" / "sample_rss.xml"
    client = _DummyClient(xml_text.read_text(encoding="utf-8"))
    item = fetch_rss_items(client, rss_url="https://example.invalid/feed", limit=1)[0]

    normalized = normalize_rss_item(item)

    assert normalized.source == "techcrunch"
    assert normalized.source_record_id == "tc-fixture-guid-1"
    assert normalized.url == "https://techcrunch.com/2026/02/01/example/"
    assert normalized.published_at is not None
    assert "$OPENAI" in normalized.entities

from __future__ import annotations

from datetime import datetime, timezone

from .extract import extract_investment_signal
from .filter import is_relevant
from .ingest import fetch_article_text
from .models import Article, IntelRecord


def build_intel_records(
    articles: list[Article],
    *,
    fetch_full_text: bool = False,
) -> list[IntelRecord]:
    out: list[IntelRecord] = []
    extracted_at = datetime.now(timezone.utc)
    for a in articles:
        if not is_relevant(a):
            continue
        full_text = fetch_article_text(a.url, enabled=fetch_full_text)
        signal = extract_investment_signal(a, full_text=full_text)
        # For KG output, we need at least a Company entity.
        if not (signal.company and signal.company.strip()):
            continue
        out.append(IntelRecord(article=a, investment=signal, extracted_at=extracted_at))
    return out

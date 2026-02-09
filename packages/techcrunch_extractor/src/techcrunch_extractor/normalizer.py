from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
import re

from .fetcher import TechCrunchRssItem
from .types import InvestmentIntelItem


_TICKER_RE = re.compile(r"\$[A-Z]{1,6}\b")


def normalize_rss_item(item: TechCrunchRssItem) -> InvestmentIntelItem:
    published_at = None
    if item.pub_date:
        try:
            published_at = parsedate_to_datetime(item.pub_date)
        except Exception:
            published_at = None

    entities: list[str] = []
    if item.title:
        entities.extend([m.group(0) for m in _TICKER_RE.finditer(item.title)])

    tags = list(dict.fromkeys(item.categories))
    return InvestmentIntelItem(
        source="techcrunch",
        source_record_type="rss_item",
        source_record_id=item.guid,
        url=item.link,
        title=item.title,
        summary=item.description,
        published_at=published_at,
        entities=entities,
        tags=tags,
        raw={
            "guid": item.guid,
            "link": item.link,
            "title": item.title,
            "description": item.description,
            "pub_date": item.pub_date,
            "categories": item.categories,
            "author": item.author,
        },
    )

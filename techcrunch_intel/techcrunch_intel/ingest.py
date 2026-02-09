from __future__ import annotations

from datetime import datetime, timezone
import time
from typing import Any

import feedparser
import httpx

from .models import Article


def fetch_rss_entries(
    rss_url: str,
    *,
    limit: int = 50,
    user_agent: str = "techcrunch-intel/0.1 (educational)",
    timeout_s: float = 30.0,
) -> list[Article]:
    """Fetch and parse a TechCrunch RSS feed into `Article` objects.

    Notes:
    - RSS is the intended access path.
    - Keep `limit` modest and cache in real usage.
    """

    resp = httpx.get(rss_url, headers={"User-Agent": user_agent}, timeout=timeout_s)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    entries = list(parsed.entries or [])
    out: list[Article] = []
    for e in entries[: max(0, int(limit))]:
        out.append(_entry_to_article(e))
    return out


def fetch_article_text(
    url: str,
    *,
    enabled: bool = False,
    user_agent: str = "techcrunch-intel/0.1 (educational)",
    timeout_s: float = 30.0,
) -> str | None:
    """Optional HTML fetch for additional extraction.

    Disabled by default; RSS metadata is the primary ingestion method.
    """
    if not enabled:
        return None

    resp = httpx.get(url, headers={"User-Agent": user_agent}, timeout=timeout_s)
    resp.raise_for_status()
    html = resp.text

    try:
        from bs4 import BeautifulSoup
    except Exception:
        return None

    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article")
    if article is None:
        return None
    text = article.get_text("\n", strip=True)
    return text or None


def _entry_to_article(entry: Any) -> Article:
    title = str(getattr(entry, "title", "") or "").strip()
    url = str(getattr(entry, "link", "") or "").strip()
    summary = str(getattr(entry, "summary", "") or "").strip() or None

    author = None
    if getattr(entry, "author", None):
        author = str(entry.author).strip() or None

    guid = None
    if getattr(entry, "id", None):
        guid = str(entry.id).strip() or None

    categories: list[str] = []
    for t in (getattr(entry, "tags", None) or []):
        term = (t or {}).get("term") if isinstance(t, dict) else getattr(t, "term", None)
        if term:
            categories.append(str(term))

    published_at = _parse_published_at(entry)

    return Article(
        title=title,
        url=url,
        published_at=published_at,
        summary=summary,
        author=author,
        categories=categories,
        guid=guid,
    )


def _parse_published_at(entry: Any) -> datetime | None:
    parsed_struct = None
    for key in ("published_parsed", "updated_parsed"):
        try:
            parsed_struct = entry.get(key)
        except Exception:
            parsed_struct = getattr(entry, key, None)
        if parsed_struct:
            break

    if parsed_struct:
        try:
            return datetime.fromtimestamp(time.mktime(parsed_struct), tz=timezone.utc)
        except Exception:
            pass

    # Fallback to string parsing.
    val = None
    for key in ("published", "updated"):
        try:
            val = entry.get(key)
        except Exception:
            val = getattr(entry, key, None)
        if val:
            break
    if not val:
        return None

    s = str(val)
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    return None

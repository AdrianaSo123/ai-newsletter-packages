from __future__ import annotations

from datetime import datetime, timezone
import re

from .fetcher import RedditPost
from .types import InvestmentIntelItem


_TICKER_RE = re.compile(r"(?:\$|\b)([A-Z]{2,6})\b")
_FUNDING_KEYWORDS = (
    "seed",
    "series a",
    "series b",
    "series c",
    "raised",
    "funding",
    "round",
    "valuation",
    "acquisition",
    "acquired",
    "ipo",
)


def normalize_post(post: RedditPost) -> InvestmentIntelItem:
    published_at = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
    url = "https://www.reddit.com" + post.permalink if post.permalink.startswith("/") else post.url
    text = (post.title or "") + "\n" + (post.selftext or "")

    tickers = sorted({m.group(1) for m in _TICKER_RE.finditer(text)})
    tags: list[str] = []
    lower = text.lower()
    if any(k in lower for k in _FUNDING_KEYWORDS):
        tags.append("financing")

    entities = [f"TICKER:{t}" for t in tickers]
    return InvestmentIntelItem(
        source="reddit",
        source_record_type="post",
        source_record_id=post.fullname,
        url=url,
        title=post.title,
        summary=(post.selftext[:5000] if post.selftext else None),
        published_at=published_at,
        entities=entities,
        tags=tags,
        raw={
            "id": post.id,
            "fullname": post.fullname,
            "subreddit": post.subreddit,
            "author": post.author,
            "score": post.score,
            "num_comments": post.num_comments,
            "permalink": post.permalink,
            "url": post.url,
        },
    )

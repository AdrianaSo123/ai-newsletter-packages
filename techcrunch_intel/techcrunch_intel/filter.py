from __future__ import annotations

from .keywords import is_ai_related_text
from .models import Article

FUNDING_KEYWORDS = (
    "raises",
    "raised",
    "lands",
    "secures",
    "closes",
    "funding",
    "seed",
    "pre-seed",
    "series a",
    "series b",
    "series c",
    "series d",
    "series e",
    "round",
    "valuation",
    "backed by",
    "led by",
    "participation from",
)

MNA_KEYWORDS = (
    "acquires",
    "acquired",
    "acquisition",
)


def is_ai_related(article: Article) -> bool:
    text = _article_text(article)
    return is_ai_related_text(text)


def is_investment_related(article: Article) -> bool:
    text = _article_text(article)
    return any(k in text for k in FUNDING_KEYWORDS) or any(k in text for k in MNA_KEYWORDS)


def is_relevant(article: Article) -> bool:
    return is_ai_related(article) and is_investment_related(article)


def _article_text(article: Article) -> str:
    blob = "\n".join(
        [
            article.title or "",
            article.summary or "",
            " ".join(article.categories or []),
        ]
    )
    # `keywords.is_ai_related_text()` handles case normalization.
    return blob

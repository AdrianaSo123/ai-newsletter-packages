from __future__ import annotations

import re

from .models import Article, InvestmentSignal
from .keywords import is_ai_related_text


_AMOUNT_RE = re.compile(
    r"(?P<currency>\$|€|£)\s?(?P<value>\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s?(?P<unit>k|m|b|thousand|million|billion)?\b",
    re.IGNORECASE,
)

_STAGE_RE = re.compile(
    r"\b(seed|pre-seed|series\s+[a-h]|series\s+[a-h]\+|series\s+[a-h]\s+extension)\b",
    re.IGNORECASE,
)

_RAISES_TITLE_RE = re.compile(
    r"^(?P<company>.+?)\s+(raises|raised|lands|secures|closes)\b",
    re.IGNORECASE,
)

_ACQUIRES_TITLE_RE = re.compile(
    r"^(?P<company>.+?)\s+(acquires|acquired|buys|to\s+buy)\b",
    re.IGNORECASE,
)

_FUNDLIKE_RE = re.compile(r"\b(fund|funds)\b", re.IGNORECASE)


def extract_investment_signal(article: Article, *, full_text: str | None = None) -> InvestmentSignal:
    """Best-effort extraction from RSS title/summary (and optionally fetched full text)."""

    text = "\n".join([article.title or "", article.summary or "", full_text or ""]).strip()
    ai_context = "\n".join(
        [
            article.title or "",
            article.summary or "",
            " ".join(article.categories or []),
            full_text or "",
        ]
    )
    ai_relevant = is_ai_related_text(ai_context)

    company = _extract_company(article.title)
    amount_text = _extract_amount(text)
    stage = _extract_stage(text)
    investors = _extract_investors(text)

    notes = None
    if _FUNDLIKE_RE.search(text) is not None and ("raises" in (article.title or "").lower() or "raised" in (article.title or "").lower()):
        # Transparent annotation for stories about fund managers raising funds.
        notes = "fund_raise_story"

    return InvestmentSignal(
        ai_relevant=ai_relevant,
        company=company,
        amount_text=amount_text,
        stage=stage,
        investors=investors,
        notes=notes,
    )


def _extract_amount(text: str) -> str | None:
    m = _AMOUNT_RE.search(text)
    if not m:
        return None
    cur = m.group("currency")
    val = m.group("value")
    unit = m.group("unit")
    unit_norm = (unit or "").strip()
    return f"{cur}{val}{unit_norm}" if unit_norm else f"{cur}{val}"


def _extract_stage(text: str) -> str | None:
    m = _STAGE_RE.search(text)
    if not m:
        return None
    return m.group(1).strip().lower()


def _extract_company(title: str) -> str | None:
    if not title:
        return None
    t = title.strip()

    m = _RAISES_TITLE_RE.search(t)
    if m:
        company = m.group("company").strip()
    else:
        m2 = _ACQUIRES_TITLE_RE.search(t)
        if not m2:
            return None
        company = m2.group("company").strip()

    # Avoid grabbing prefixes like "Exclusive:" etc.
    company = re.sub(r"^(exclusive:|report:)\s*", "", company, flags=re.IGNORECASE).strip()
    return company or None


def _extract_investors(text: str) -> list[str]:
    investors: list[str] = []

    # Very lightweight patterns.
    # Example: "... led by Sequoia Capital with participation from ..."
    for marker in ("led by", "participation from", "backed by"):
        frag = _slice_after_ci(text, marker)
        if frag:
            investors.extend(_split_org_list(frag))

    # De-dup while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for inv in investors:
        inv2 = inv.strip(" ,.;:-\n\t").strip()
        if not inv2:
            continue
        if inv2 in seen:
            continue
        seen.add(inv2)
        out.append(inv2)
    return out


def _slice_after(text: str, marker: str) -> str | None:
    idx = text.find(marker)
    if idx < 0:
        return None
    frag = text[idx + len(marker) :]
    # stop at first sentence-ish boundary
    for stop in (". ", "\n", ")", ";"):
        sidx = frag.find(stop)
        if sidx >= 0:
            frag = frag[:sidx]
            break
    return frag.strip() or None


def _slice_after_ci(text: str, marker: str) -> str | None:
    """Case-insensitive slice-after that preserves the original text casing."""
    m = re.search(re.escape(marker), text, flags=re.IGNORECASE)
    if not m:
        return None
    frag = text[m.end() :]
    for stop in (". ", "\n", ")", ";"):
        sidx = frag.find(stop)
        if sidx >= 0:
            frag = frag[:sidx]
            break
    return frag.strip() or None


def _split_org_list(fragment: str) -> list[str]:
    # Split on commas and 'and'
    frag = fragment
    frag = frag.replace(" and ", ",")
    parts = [p.strip() for p in frag.split(",")]
    # Remove leading filler words
    cleaned: list[str] = []
    for p in parts:
        p2 = re.sub(r"^(including|such as)\s+", "", p.strip(), flags=re.IGNORECASE)
        if p2:
            cleaned.append(p2)
    return cleaned

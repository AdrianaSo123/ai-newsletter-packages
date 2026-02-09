from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence


DEFAULT_AI_PHRASES: tuple[str, ...] = (
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "neural network",
    "generative ai",
    "genai",
    "large language model",
    "large language models",
    "llm",
    "foundation model",
    "foundation models",
)

DEFAULT_AI_TOKENS: tuple[str, ...] = (
    "ai",
)


@dataclass(frozen=True)
class KeywordMatcher:
    """Transparent, rule-based keyword/phrase matching.

    - `phrases` are matched as case-insensitive substrings.
    - `tokens` are matched as case-insensitive whole tokens using word boundaries.
    """

    phrases: tuple[str, ...] = DEFAULT_AI_PHRASES
    tokens: tuple[str, ...] = DEFAULT_AI_TOKENS

    def matches(self, text: str) -> bool:
        if not text:
            return False
        haystack = text.lower()
        for p in self.phrases:
            if p and p.lower() in haystack:
                return True

        for t in self.tokens:
            t2 = (t or "").strip()
            if not t2:
                continue
            # Whole-token match for short tokens like "ai" to avoid false positives
            # such as "laid", "chair", etc.
            pat = re.compile(rf"\b{re.escape(t2.lower())}\b", re.IGNORECASE)
            if pat.search(text) is not None:
                return True

        return False


def default_ai_matcher() -> KeywordMatcher:
    return KeywordMatcher()


def is_ai_related_text(
    text: str,
    *,
    matcher: KeywordMatcher | None = None,
) -> bool:
    """Rule-based AI relevance check for arbitrary text."""

    m = matcher or default_ai_matcher()
    return m.matches(text)

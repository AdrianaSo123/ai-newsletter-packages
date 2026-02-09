from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class RateLimitInfo:
    used: float | None
    remaining: float | None
    reset_seconds: float | None


class RedditApi(Protocol):
    def get_json(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> tuple[dict[str, Any], RateLimitInfo]:
        """Fetch JSON from an OAuth-authenticated Reddit endpoint."""

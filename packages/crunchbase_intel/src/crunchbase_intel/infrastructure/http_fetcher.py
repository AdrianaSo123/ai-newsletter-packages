from __future__ import annotations

import time

import httpx

from ..domain.errors import FetchError


class PoliteHttpFetcher:
    """Minimal, rate-limited fetcher for public pages.

    This is intentionally conservative:
    - single request at a time
    - minimum delay between requests
    - no cookies, no authenticated sessions
    """

    def __init__(
        self,
        *,
        timeout_s: float = 30.0,
        user_agent: str = "crunchbase-intel/0.1.0 (academic; minimal)",
        min_delay_s: float = 1.0,
    ) -> None:
        self._client = httpx.Client(
            timeout=timeout_s,
            headers={"User-Agent": user_agent},
            follow_redirects=True,
        )
        self._min_delay_s = max(0.0, float(min_delay_s))
        self._last_request_t: float | None = None

    def get_text(self, url: str) -> str:
        now = time.time()
        if self._last_request_t is not None:
            sleep_for = self._min_delay_s - (now - self._last_request_t)
            if sleep_for > 0:
                time.sleep(sleep_for)

        try:
            resp = self._client.get(url)
        except httpx.RequestError as exc:
            raise FetchError(
                f"Network error fetching {url}: {exc}",
                url=url,
                status_code=None,
                kind="network_error",
            ) from exc
        finally:
            self._last_request_t = time.time()

        if resp.status_code in (401, 403):
            raise FetchError(
                f"Access denied fetching {url} (HTTP {resp.status_code}). Public access may be restricted.",
                url=url,
                status_code=resp.status_code,
                kind="access_denied",
            )
        if resp.status_code == 429:
            raise FetchError(
                f"Rate limited fetching {url} (HTTP 429). Try again later; do not increase request rate.",
                url=url,
                status_code=429,
                kind="rate_limited",
            )

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise FetchError(
                f"HTTP error fetching {url}: {resp.status_code}. Body: {resp.text[:2000]!r}",
                url=url,
                status_code=resp.status_code,
                kind="http_error",
            ) from exc

        text = resp.text or ""
        if not text.strip():
            raise FetchError(
                f"Empty response fetching {url}.",
                url=url,
                status_code=resp.status_code,
                kind="empty_response",
            )
        return text

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PoliteHttpFetcher":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

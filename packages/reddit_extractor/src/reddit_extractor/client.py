from __future__ import annotations

import os
import time
from typing import Any

import httpx

from .config import RedditAuthConfig
from .ports import RateLimitInfo


class RedditAuthError(RuntimeError):
    pass

class RedditApiError(RuntimeError):
    pass


class RedditClient:
    """Minimal Reddit OAuth client.

    Supported auth:
    - Provide `REDDIT_ACCESS_TOKEN` (best for PoC)
    - Or provide `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_REFRESH_TOKEN`
      to refresh an access token.
    """

    def __init__(
        self,
        *,
        config: RedditAuthConfig | None = None,
        access_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        refresh_token: str | None = None,
        user_agent: str | None = None,
        timeout_s: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        if config is None:
            config = RedditAuthConfig.from_env()

        self._access_token = access_token or config.access_token
        self._client_id = client_id or config.client_id
        self._client_secret = client_secret or config.client_secret
        self._refresh_token = refresh_token or config.refresh_token
        self._user_agent = user_agent or config.user_agent
        self._max_retries = max(0, int(max_retries))

        if not self._user_agent:
            raise RedditAuthError(
                "Missing Reddit User-Agent. Set REDDIT_USER_AGENT to a unique value like "
                "'<platform>:<app id>:<version> (by /u/<username>)'."
            )

        self._http = httpx.Client(timeout=timeout_s, headers={"User-Agent": self._user_agent})

    def _ensure_token(self) -> str:
        if self._access_token:
            return self._access_token
        if self._client_id and self._client_secret and self._refresh_token:
            self._access_token = self.refresh_access_token()
            return self._access_token
        raise RedditAuthError(
            "Missing access token. Set REDDIT_ACCESS_TOKEN or provide "
            "REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET/REDDIT_REFRESH_TOKEN."
        )

    def refresh_access_token(self) -> str:
        if not (self._client_id and self._client_secret and self._refresh_token):
            raise RedditAuthError("Refresh-token flow requires client_id, client_secret, refresh_token")
        resp = self._request_with_retries(
            "POST",
            "https://www.reddit.com/api/v1/access_token",
            auth=(self._client_id, self._client_secret),
            data={"grant_type": "refresh_token", "refresh_token": self._refresh_token},
            headers={"User-Agent": self._user_agent},
        )
        data = resp.json()
        token = data.get("access_token")
        if not token:
            raise RedditAuthError(f"Unexpected token response: {data}")
        return token

    def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> tuple[dict[str, Any], RateLimitInfo]:
        token = self._ensure_token()
        url = "https://oauth.reddit.com" + path
        resp = self._request_with_retries(
            "GET",
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}", "User-Agent": self._user_agent},
        )
        rl = RateLimitInfo(
            used=_to_float(resp.headers.get("X-Ratelimit-Used")),
            remaining=_to_float(resp.headers.get("X-Ratelimit-Remaining")),
            reset_seconds=_to_float(resp.headers.get("X-Ratelimit-Reset")),
        )
        return resp.json(), rl

    def _request_with_retries(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._http.request(method, url, **kwargs)
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise RedditApiError(f"Network error calling Reddit: {exc}") from exc
                time.sleep(0.5 * (attempt + 1))
                continue

            if resp.status_code in (401, 403):
                detail = _safe_detail(resp)
                raise RedditAuthError(
                    "Reddit authentication failed (401/403). "
                    "Verify REDDIT_ACCESS_TOKEN (or refresh-token env vars) and REDDIT_USER_AGENT. "
                    f"Details: {detail}"
                )

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < self._max_retries:
                    retry_after = _to_float(resp.headers.get("Retry-After"))
                    time.sleep(retry_after if retry_after is not None else 0.5 * (attempt + 1))
                    continue

            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = _safe_detail(resp)
                raise RedditApiError(
                    f"Reddit API error {resp.status_code} for {method} {url}. Details: {detail}"
                ) from exc

            return resp

        assert last_exc is not None
        raise RedditApiError(f"Reddit request failed: {last_exc}")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "RedditClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _to_float(val: str | None) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except Exception:
        return None


def _safe_detail(resp: httpx.Response) -> str:
    try:
        text = resp.text
    except Exception:
        return "<no response body>"
    text = (text or "").strip()
    return text[:5000] if text else "<empty response body>"

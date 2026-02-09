from __future__ import annotations

import time
from typing import Any

import httpx

from .config import CrunchbaseConfig


class CrunchbaseAuthError(RuntimeError):
    pass


class CrunchbaseApiError(RuntimeError):
    pass


class CrunchbaseClient:
    def __init__(
        self,
        *,
        config: CrunchbaseConfig | None = None,
        user_key: str | None = None,
        base_url: str = "https://api.crunchbase.com/v4/data",
        timeout_s: float = 30.0,
    ) -> None:
        if config is None:
            config = CrunchbaseConfig.from_env()

        self._user_key = user_key or config.user_key
        if not self._user_key:
            raise CrunchbaseAuthError("Missing CRUNCHBASE_USER_KEY")
        self._base_url = (base_url or config.base_url).rstrip("/")
        self._http = httpx.Client(timeout=timeout_s)
        self._max_retries = 2

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self._base_url + path
        merged = {"user_key": self._user_key}
        if params:
            merged.update(params)
        resp = self._request_with_retries("GET", url, params=merged)
        return resp.json()

    def post(self, path: str, *, json_body: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self._base_url + path
        merged = {"user_key": self._user_key}
        if params:
            merged.update(params)
        resp = self._request_with_retries("POST", url, params=merged, json=json_body)
        return resp.json()

    def _request_with_retries(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._http.request(method, url, **kwargs)
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise CrunchbaseApiError(f"Network error calling Crunchbase: {exc}") from exc
                time.sleep(0.5 * (attempt + 1))
                continue

            if resp.status_code == 429 or resp.status_code >= 500:
                if attempt < self._max_retries:
                    retry_after = _to_float(resp.headers.get("Retry-After"))
                    time.sleep(retry_after if retry_after is not None else 0.5 * (attempt + 1))
                    continue

            if resp.status_code in (401, 403):
                raise CrunchbaseAuthError(
                    "Crunchbase authentication failed (401/403). Check CRUNCHBASE_USER_KEY and plan access. "
                    f"Details: {_safe_detail(resp)}"
                )

            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise CrunchbaseApiError(
                    f"Crunchbase API error {resp.status_code} for {method} {url}. Details: {_safe_detail(resp)}"
                ) from exc

            return resp

        assert last_exc is not None
        raise CrunchbaseApiError(f"Crunchbase request failed: {last_exc}")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "CrunchbaseClient":
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

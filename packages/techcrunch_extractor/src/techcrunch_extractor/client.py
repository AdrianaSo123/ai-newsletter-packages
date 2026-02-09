from __future__ import annotations

import httpx


DEFAULT_USER_AGENT = "techcrunch-extractor/0.1.0"


class TechCrunchClient:
    def __init__(self, *, timeout_s: float = 30.0, user_agent: str | None = None) -> None:
        headers = {"User-Agent": (user_agent or DEFAULT_USER_AGENT)}
        self._client = httpx.Client(timeout=timeout_s, headers=headers)

    def get_text(self, url: str, *, params: dict[str, str] | None = None) -> str:
        resp = self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.text

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "TechCrunchClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

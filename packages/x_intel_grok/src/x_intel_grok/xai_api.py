from __future__ import annotations

import httpx

from .config import XAiConfig


class XAiError(RuntimeError):
    pass


def chat_completion(*, cfg: XAiConfig, messages: list[dict], temperature: float = 0.0) -> dict:
    base = cfg.base_url.rstrip("/")
    url = base + "/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    payload: dict = {
        "model": cfg.model or "grok",
        "messages": messages,
        "temperature": temperature,
        # Many OpenAI-compatible providers support JSON response formatting.
        # If unsupported, the provider may ignore it.
        "response_format": {"type": "json_object"},
    }

    with httpx.Client(timeout=60.0, follow_redirects=True, headers=headers) as client:
        resp = client.post(url, json=payload)
    if resp.status_code >= 400:
        raise XAiError(
            f"xAI request failed status={resp.status_code} url={url!r} body={resp.text[:300]!r}"
        )
    return resp.json()

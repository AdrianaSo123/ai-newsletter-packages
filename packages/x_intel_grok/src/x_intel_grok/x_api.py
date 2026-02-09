from __future__ import annotations

import httpx

from .config import XApiConfig


class XApiError(RuntimeError):
    pass


def fetch_tweets(*, cfg: XApiConfig, tweet_ids: list[str]) -> dict:
    if not tweet_ids:
        return {"data": []}

    url = cfg.base_url.rstrip("/") + "/tweets"
    params = {
        "ids": ",".join(tweet_ids),
        # `text` is typically present by default, but include it explicitly.
        "tweet.fields": "text,created_at,lang,author_id,public_metrics",
        "expansions": "author_id",
        "user.fields": "username,name,verified",
    }
    headers = {
        "Authorization": f"Bearer {cfg.bearer_token}",
        "User-Agent": cfg.user_agent,
    }

    with httpx.Client(timeout=30.0, follow_redirects=True, headers=headers) as client:
        resp = client.get(url, params=params)
    if resp.status_code >= 400:
        raise XApiError(
            f"X API request failed status={resp.status_code} url={url!r} body={resp.text[:300]!r}"
        )
    return resp.json()

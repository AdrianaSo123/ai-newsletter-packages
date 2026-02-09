from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ports import RateLimitInfo, RedditApi


@dataclass(frozen=True)
class RedditPost:
    id: str
    fullname: str
    subreddit: str
    title: str
    selftext: str
    permalink: str
    url: str
    created_utc: float
    author: str | None
    score: int | None
    num_comments: int | None


def search_posts(
    client: RedditApi,
    *,
    subreddit: str,
    query: str,
    limit: int = 25,
    sort: str = "new",
    time_filter: str = "month",
) -> tuple[list[RedditPost], RateLimitInfo]:
    data, rl = client.get_json(
        f"/r/{subreddit}/search",
        params={
            "q": query,
            "restrict_sr": 1,
            "sort": sort,
            "t": time_filter,
            "limit": min(limit, 100),
            "raw_json": 1,
        },
    )
    posts = _parse_listing_posts(data)
    return posts[:limit], rl


def fetch_new_posts(
    client: RedditApi,
    *,
    subreddit: str,
    limit: int = 25,
) -> tuple[list[RedditPost], RateLimitInfo]:
    data, rl = client.get_json(
        f"/r/{subreddit}/new",
        params={"limit": min(limit, 100), "raw_json": 1},
    )
    posts = _parse_listing_posts(data)
    return posts[:limit], rl


def _parse_listing_posts(data: dict[str, Any]) -> list[RedditPost]:
    children = (((data or {}).get("data") or {}).get("children") or [])
    posts: list[RedditPost] = []
    for child in children:
        if not isinstance(child, dict) or child.get("kind") != "t3":
            continue
        d = child.get("data") or {}
        post_id = str(d.get("id") or "")
        fullname = str(d.get("name") or "")
        if not post_id or not fullname:
            continue
        posts.append(
            RedditPost(
                id=post_id,
                fullname=fullname,
                subreddit=str(d.get("subreddit") or ""),
                title=str(d.get("title") or ""),
                selftext=str(d.get("selftext") or ""),
                permalink=str(d.get("permalink") or ""),
                url=str(d.get("url") or ""),
                created_utc=float(d.get("created_utc") or 0.0),
                author=(str(d.get("author")) if d.get("author") is not None else None),
                score=(int(d.get("score")) if d.get("score") is not None else None),
                num_comments=(int(d.get("num_comments")) if d.get("num_comments") is not None else None),
            )
        )
    return posts

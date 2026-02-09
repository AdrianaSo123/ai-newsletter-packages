from __future__ import annotations

import re


_STATUS_RE = re.compile(r"/status/(?P<id>\d+)")


def tweet_id_from_url(url: str) -> str:
    """Extract tweet ID from an X/Twitter status URL."""
    m = _STATUS_RE.search(url or "")
    if not m:
        raise ValueError("Unrecognized tweet URL; expected .../status/<digits>")
    return m.group("id")

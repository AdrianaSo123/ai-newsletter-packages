from __future__ import annotations

import pytest

from x_intel_grok.url import tweet_id_from_url


def test_tweet_id_from_url_extracts_id() -> None:
    assert tweet_id_from_url("https://x.com/someone/status/1234567890") == "1234567890"


def test_tweet_id_from_url_rejects_non_status() -> None:
    with pytest.raises(ValueError):
        tweet_id_from_url("https://x.com/someone")

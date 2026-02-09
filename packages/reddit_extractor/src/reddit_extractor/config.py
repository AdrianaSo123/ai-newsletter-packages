from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


class RedditConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class RedditAuthConfig:
    user_agent: str
    access_token: str | None = None
    client_id: str | None = None
    client_secret: str | None = None
    refresh_token: str | None = None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "RedditAuthConfig":
        env = os.environ if environ is None else environ
        user_agent = (env.get("REDDIT_USER_AGENT") or "").strip()
        if not user_agent:
            raise RedditConfigError(
                "Missing REDDIT_USER_AGENT. Set it to a unique value like "
                "'<platform>:<app id>:<version> (by /u/<username>)'."
            )

        access_token = (env.get("REDDIT_ACCESS_TOKEN") or "").strip() or None
        client_id = (env.get("REDDIT_CLIENT_ID") or "").strip() or None
        client_secret = (env.get("REDDIT_CLIENT_SECRET") or "").strip() or None
        refresh_token = (env.get("REDDIT_REFRESH_TOKEN") or "").strip() or None

        return cls(
            user_agent=user_agent,
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
        )

    def has_any_token_source(self) -> bool:
        if self.access_token:
            return True
        return bool(self.client_id and self.client_secret and self.refresh_token)

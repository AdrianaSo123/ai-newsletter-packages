from __future__ import annotations

import secrets
import urllib.parse
from dataclasses import dataclass
from typing import Iterable

import httpx


REDDIT_AUTHORIZE_URL = "https://www.reddit.com/api/v1/authorize"
REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"


@dataclass(frozen=True)
class OAuthTokenResponse:
    access_token: str
    token_type: str | None = None
    expires_in: int | None = None
    scope: str | None = None
    refresh_token: str | None = None


def generate_state(nbytes: int = 16) -> str:
    return secrets.token_urlsafe(nbytes)


def build_authorize_url(
    *,
    client_id: str,
    redirect_uri: str,
    state: str,
    scope: Iterable[str],
    duration: str = "permanent",
) -> str:
    params = {
        "client_id": client_id,
        "response_type": "code",
        "state": state,
        "redirect_uri": redirect_uri,
        "duration": duration,
        "scope": " ".join(scope),
    }
    return REDDIT_AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)


def exchange_code_for_tokens(
    *,
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
    user_agent: str,
    timeout_s: float = 30.0,
) -> OAuthTokenResponse:
    """Exchange a one-time authorization code for tokens.

    If the authorization request used `duration=permanent`, Reddit returns a
    `refresh_token` which you can store as `REDDIT_REFRESH_TOKEN`.
    """

    resp = httpx.post(
        REDDIT_TOKEN_URL,
        auth=(client_id, client_secret),
        data={"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri},
        headers={"User-Agent": user_agent},
        timeout=timeout_s,
    )
    resp.raise_for_status()
    data = resp.json()

    access_token = data.get("access_token")
    if not access_token:
        raise RuntimeError(f"Unexpected token response: {data}")

    return OAuthTokenResponse(
        access_token=str(access_token),
        token_type=data.get("token_type"),
        expires_in=data.get("expires_in"),
        scope=data.get("scope"),
        refresh_token=data.get("refresh_token"),
    )

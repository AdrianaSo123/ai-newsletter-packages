from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


class XIntelGrokConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class XApiConfig:
    bearer_token: str
    base_url: str = "https://api.x.com/2"
    user_agent: str = "macos:x-intel-grok:0.1.0"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "XApiConfig":
        env = os.environ if environ is None else environ
        bearer = (env.get("X_BEARER_TOKEN") or "").strip()
        if not bearer:
            raise XIntelGrokConfigError("Missing X_BEARER_TOKEN")
        base_url = (env.get("X_API_BASE_URL") or "").strip() or cls.base_url
        user_agent = (env.get("X_USER_AGENT") or "").strip() or cls.user_agent
        return cls(bearer_token=bearer, base_url=base_url, user_agent=user_agent)


@dataclass(frozen=True)
class XAiConfig:
    api_key: str
    base_url: str = "https://api.x.ai"
    model: str | None = None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "XAiConfig":
        env = os.environ if environ is None else environ
        api_key = (env.get("XAI_API_KEY") or "").strip()
        if not api_key:
            raise XIntelGrokConfigError("Missing XAI_API_KEY")
        base_url = (env.get("XAI_BASE_URL") or "").strip() or cls.base_url
        model = (env.get("XAI_MODEL") or "").strip() or None
        return cls(api_key=api_key, base_url=base_url, model=model)

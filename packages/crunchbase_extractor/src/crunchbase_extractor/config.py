from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


class CrunchbaseConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class CrunchbaseConfig:
    user_key: str
    base_url: str = "https://api.crunchbase.com/v4/data"

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "CrunchbaseConfig":
        env = os.environ if environ is None else environ
        user_key = (env.get("CRUNCHBASE_USER_KEY") or "").strip()
        if not user_key:
            raise CrunchbaseConfigError("Missing CRUNCHBASE_USER_KEY")
        base_url = (env.get("CRUNCHBASE_BASE_URL") or "").strip() or cls.base_url
        return cls(user_key=user_key, base_url=base_url)

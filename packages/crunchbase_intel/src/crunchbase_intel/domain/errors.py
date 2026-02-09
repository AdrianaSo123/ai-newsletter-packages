from __future__ import annotations


class CrunchbaseIntelError(RuntimeError):
    """Base error for this package.

    Raised for explicit, user-actionable failures. We prefer raising a specific
    error over returning partial/ambiguous results.
    """


class InvalidInputError(CrunchbaseIntelError):
    """Raised when caller-provided inputs are invalid."""


class FetchError(CrunchbaseIntelError):
    """Raised when live fetching fails (network, access denied, rate limit)."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        status_code: int | None = None,
        kind: str = "fetch_error",
    ) -> None:
        super().__init__(message)
        self.url = url
        self.status_code = status_code
        self.kind = kind


class ParseError(CrunchbaseIntelError):
    """Raised when HTML parsing fails unexpectedly."""

from __future__ import annotations

from urllib.parse import urlparse

from .errors import InvalidInputError


def validate_org_url(url: str) -> str:
    """Validate that a URL looks like a Crunchbase organization page.

    We intentionally restrict inputs to avoid accidentally interpreting unrelated
    pages (e.g., news sections) as company records.

    Accepted shapes:
    - https://www.crunchbase.com/organization/<slug>
    - https://crunchbase.com/organization/<slug>

    This is not a guarantee the page is accessible; it only enforces intent.
    """

    u = (url or "").strip()
    if not u:
        raise InvalidInputError("Missing URL")

    parsed = urlparse(u)
    if parsed.scheme not in ("http", "https"):
        raise InvalidInputError(f"Unsupported URL scheme: {parsed.scheme!r}")

    host = (parsed.netloc or "").lower()
    if host in ("crunchbase.com", "www.crunchbase.com"):
        pass
    else:
        raise InvalidInputError(
            "Unsupported host for org extraction. Expected crunchbase.com organization URL; "
            f"got host={host!r}."
        )

    path = parsed.path or ""
    if not path.startswith("/organization/"):
        raise InvalidInputError(
            "URL does not look like a Crunchbase organization page. "
            "Expected path starting with '/organization/'."
        )

    # Require at least one non-empty path segment after /organization/
    slug = path[len("/organization/") :].strip("/")
    if not slug:
        raise InvalidInputError("Organization URL is missing the organization slug.")

    return u

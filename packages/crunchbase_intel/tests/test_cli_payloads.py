from __future__ import annotations

import json

from crunchbase_intel.domain.errors import FetchError


def test_fetch_error_has_structured_fields() -> None:
    err = FetchError(
        "Access denied",
        url="https://www.crunchbase.com/organization/anthropic",
        status_code=403,
        kind="access_denied",
    )
    payload = {
        "ok": False,
        "error": {
            "type": err.__class__.__name__,
            "message": str(err),
            "kind": err.kind,
            "url": err.url,
            "status_code": err.status_code,
        },
    }
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    assert decoded["error"]["kind"] == "access_denied"
    assert decoded["error"]["status_code"] == 403

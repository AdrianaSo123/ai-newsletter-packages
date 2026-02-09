from __future__ import annotations

from typing import Any, Protocol


class CrunchbaseApi(Protocol):
    def get(self, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """GET JSON from Crunchbase v4 API."""

    def post(
        self, path: str, *, json_body: dict[str, Any], params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """POST JSON to Crunchbase v4 API."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from crunchbase_extractor.cli import app


runner = CliRunner(mix_stderr=False)


def _last_json_line(stderr: str) -> dict:
    lines = [ln for ln in (stderr or "").splitlines() if ln.strip()]
    assert lines, "expected stderr output"
    return json.loads(lines[-1])


def test_autocomplete_missing_key_structured_error(monkeypatch) -> None:
    monkeypatch.delenv("CRUNCHBASE_USER_KEY", raising=False)
    monkeypatch.delenv("CRUNCHBASE_BASE_URL", raising=False)

    result = runner.invoke(app, ["autocomplete", "--query", "airbnb"], catch_exceptions=False)

    assert result.exit_code == 2
    payload = _last_json_line(result.stderr)
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "config_error"


def test_organization_missing_key_structured_error(monkeypatch) -> None:
    monkeypatch.delenv("CRUNCHBASE_USER_KEY", raising=False)

    result = runner.invoke(app, ["organization", "--permalink", "tesla-motors"], catch_exceptions=False)

    assert result.exit_code == 2
    payload = _last_json_line(result.stderr)
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "config_error"

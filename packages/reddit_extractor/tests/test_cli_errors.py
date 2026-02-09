from __future__ import annotations

import json

from typer.testing import CliRunner

from reddit_extractor.cli import app


runner = CliRunner(mix_stderr=False)


def _last_json_line(stderr: str) -> dict:
    lines = [ln for ln in (stderr or "").splitlines() if ln.strip()]
    assert lines, "expected stderr output"
    return json.loads(lines[-1])


def test_extract_missing_user_agent_structured_error(monkeypatch) -> None:
    monkeypatch.delenv("REDDIT_USER_AGENT", raising=False)
    monkeypatch.delenv("REDDIT_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("REDDIT_REFRESH_TOKEN", raising=False)

    result = runner.invoke(app, ["extract", "--subreddit", "startups"], catch_exceptions=False)

    assert result.exit_code == 2
    payload = _last_json_line(result.stderr)
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "config_error"


def test_extract_missing_credentials_structured_error(monkeypatch) -> None:
    monkeypatch.setenv("REDDIT_USER_AGENT", "macos:test (by /u/test)")
    monkeypatch.delenv("REDDIT_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("REDDIT_REFRESH_TOKEN", raising=False)

    result = runner.invoke(app, ["extract", "--subreddit", "startups"], catch_exceptions=False)

    assert result.exit_code == 2
    payload = _last_json_line(result.stderr)
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "config_error"

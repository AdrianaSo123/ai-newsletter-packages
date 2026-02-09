from __future__ import annotations

import json

from typer.testing import CliRunner

from x_intel_grok.cli import app


runner = CliRunner(mix_stderr=False)


def test_analyze_missing_env_structured_error(monkeypatch) -> None:
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)

    result = runner.invoke(app, ["analyze", "--tweet-id", "123"], catch_exceptions=False)

    assert result.exit_code == 2
    payload = json.loads((result.stderr or "").strip().splitlines()[-1])
    assert payload["ok"] is False
    assert payload["error"]["kind"] == "config_error"

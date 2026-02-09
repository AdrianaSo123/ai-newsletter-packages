from __future__ import annotations

import os

import pytest

from typer.testing import CliRunner

from x_intel_grok.cli import app


runner = CliRunner(mix_stderr=False)


@pytest.mark.integration
def test_live_analyze_smoke_opt_in() -> None:
    """Opt-in live test.

    Set:
      - X_INTEL_GROK_INTEGRATION=1
      - X_BEARER_TOKEN=...
      - XAI_API_KEY=...
      - X_INTEL_GROK_TWEET_ID=<public tweet id you have access to>
    """

    if os.environ.get("X_INTEL_GROK_INTEGRATION") != "1":
        pytest.skip("live test is opt-in")

    tweet_id = (os.environ.get("X_INTEL_GROK_TWEET_ID") or "").strip()
    if not tweet_id:
        pytest.skip("set X_INTEL_GROK_TWEET_ID to run")

    result = runner.invoke(app, ["analyze", "--tweet-id", tweet_id], catch_exceptions=False)
    assert result.exit_code in (0, 1, 2)
    # If it succeeds, it should emit at least one JSON line to stdout.
    if result.exit_code == 0:
        assert (result.stdout or "").strip()

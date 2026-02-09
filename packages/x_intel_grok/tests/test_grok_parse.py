from __future__ import annotations

from x_intel_grok.cli import _parse_grok_json


def test_parse_grok_json_happy_path() -> None:
    resp = {"choices": [{"message": {"content": "{\"summary\": \"ok\"}"}}]}
    parsed, raw = _parse_grok_json(resp)
    assert parsed == {"summary": "ok"}
    assert raw is None


def test_parse_grok_json_falls_back_to_text() -> None:
    resp = {"choices": [{"message": {"content": "not json"}}]}
    parsed, raw = _parse_grok_json(resp)
    assert parsed is None
    assert raw == "not json"

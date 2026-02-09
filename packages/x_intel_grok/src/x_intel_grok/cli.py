from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from .config import XAiConfig, XApiConfig, XIntelGrokConfigError
from .io import emit_jsonl
from .url import tweet_id_from_url
from .x_api import XApiError, fetch_tweets
from .xai_api import XAiError, chat_completion


app = typer.Typer(add_completion=False, no_args_is_help=True)


def _emit_error(*, kind: str, message: str, code: int, command: str, details: dict | None = None) -> None:
    payload = {
        "ok": False,
        "error": {
            "kind": kind,
            "message": message,
            "command": command,
            "details": details or {},
        },
    }
    typer.echo(json.dumps(payload, ensure_ascii=False), err=True)
    raise typer.Exit(code=code)


def _parse_grok_json(grok_response: dict) -> tuple[dict | None, str | None]:
    """Try to parse the assistant content as JSON.

    Returns (parsed_json, raw_content). Exactly one should be non-None.
    """
    try:
        choices = grok_response.get("choices") or []
        msg = (choices[0] or {}).get("message") or {}
        content = msg.get("content")
        if not isinstance(content, str) or not content.strip():
            return None, None
        try:
            return json.loads(content), None
        except json.JSONDecodeError:
            return None, content
    except Exception:
        return None, None


@app.callback()
def main() -> None:
    """x-intel-grok CLI."""
    return


@app.command("analyze")
def analyze_cmd(
    tweet_url: list[str] = typer.Option(None, "--tweet-url", help="Tweet URL (repeatable)"),
    tweet_id: list[str] = typer.Option(None, "--tweet-id", help="Tweet ID (repeatable)"),
    in_file: Path | None = typer.Option(None, "--in-file", help="File with one tweet URL/ID per line"),
    out: Path | None = typer.Option(None, help="Write JSONL to this path (default: stdout)"),
) -> None:
    try:
        x_cfg = XApiConfig.from_env()
        ai_cfg = XAiConfig.from_env()
    except XIntelGrokConfigError as exc:
        _emit_error(kind="config_error", message=str(exc), code=2, command="analyze")

    ids: list[str] = []
    for u in tweet_url or []:
        try:
            ids.append(tweet_id_from_url(u))
        except ValueError as exc:
            _emit_error(kind="input_error", message=str(exc), code=2, command="analyze", details={"tweet_url": u})
    ids.extend([i.strip() for i in (tweet_id or []) if i.strip()])

    if in_file is not None:
        try:
            lines = [ln.strip() for ln in in_file.read_text(encoding="utf-8").splitlines()]
        except OSError as exc:
            _emit_error(kind="input_error", message=str(exc), code=2, command="analyze")
        for ln in lines:
            if not ln:
                continue
            if ln.isdigit():
                ids.append(ln)
            else:
                try:
                    ids.append(tweet_id_from_url(ln))
                except ValueError as exc:
                    _emit_error(kind="input_error", message=str(exc), code=2, command="analyze", details={"line": ln})

    # de-dupe while preserving order
    seen: set[str] = set()
    tweet_ids = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            tweet_ids.append(i)

    if not tweet_ids:
        _emit_error(kind="input_error", message="No tweet URLs/IDs provided", code=2, command="analyze")

    try:
        fetched = fetch_tweets(cfg=x_cfg, tweet_ids=tweet_ids)
    except XApiError as exc:
        _emit_error(kind="x_api_error", message=str(exc), code=1, command="analyze")

    data = fetched.get("data") or []
    errors = fetched.get("errors") or []
    id_to_tweet: dict[str, dict[str, Any]] = {
        t.get("id"): t for t in data if isinstance(t, dict) and t.get("id")
    }
    id_to_error: dict[str, dict[str, Any]] = {
        (e.get("resource_id") or ""): e for e in errors if isinstance(e, dict) and e.get("resource_id")
    }

    records: list[dict] = []
    for tid in tweet_ids:
        tweet = id_to_tweet.get(tid)
        if tweet is None:
            err = id_to_error.get(tid)
            records.append(
                {
                    "ok": False,
                    "tweet_id": tid,
                    "tweet_url": f"https://x.com/i/status/{tid}",
                    "error": {
                        "kind": "not_found",
                        "details": err or {},
                    },
                    "provenance": {
                        "x_api_base_url": x_cfg.base_url,
                    },
                }
            )
            continue

        text = (tweet.get("text") or "").strip()
        if not text:
            records.append(
                {
                    "ok": False,
                    "tweet_id": tid,
                    "tweet_url": f"https://x.com/i/status/{tid}",
                    "error": {"kind": "empty_text"},
                    "tweet": tweet,
                    "provenance": {"x_api_base_url": x_cfg.base_url},
                }
            )
            continue

        messages = [
            {
                "role": "system",
                "content": (
                    "You extract investment intelligence signals from social posts. "
                    "Return a single JSON object with keys: summary, entities, claims, "
                    "investment_signal (bool), confidence (0-1), and rationale."
                ),
            },
            {"role": "user", "content": text},
        ]
        try:
            grok = chat_completion(cfg=ai_cfg, messages=messages, temperature=0.0)
        except XAiError as exc:
            records.append(
                {
                    "ok": False,
                    "tweet_id": tid,
                    "tweet_url": f"https://x.com/i/status/{tid}",
                    "tweet": tweet,
                    "error": {"kind": "xai_error", "message": str(exc)},
                    "provenance": {
                        "x_api_base_url": x_cfg.base_url,
                        "xai_base_url": ai_cfg.base_url,
                        "model": ai_cfg.model or "grok",
                    },
                }
            )
            continue

        analysis_json, analysis_text = _parse_grok_json(grok)

        records.append(
            {
                "ok": True,
                "tweet_id": tid,
                "tweet_url": f"https://x.com/i/status/{tid}",
                "text": text,
                "tweet": tweet,
                "analysis": analysis_json,
                "analysis_text": analysis_text,
                "grok": grok,
                "provenance": {
                    "x_api_base_url": x_cfg.base_url,
                    "xai_base_url": ai_cfg.base_url,
                    "model": ai_cfg.model or "grok",
                },
            }
        )

    emit_jsonl(records, out)

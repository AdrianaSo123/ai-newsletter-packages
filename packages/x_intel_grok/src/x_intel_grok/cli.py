from __future__ import annotations

import json
from pathlib import Path

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
    id_to_text = {t.get("id"): (t.get("text") or "") for t in data if t.get("id")}

    records: list[dict] = []
    for tid in tweet_ids:
        text = id_to_text.get(tid)
        if text is None:
            records.append({"ok": False, "tweet_id": tid, "error": {"kind": "not_found"}})
            continue

        messages = [
            {"role": "system", "content": "You extract investment intelligence signals from social posts. Return JSON."},
            {"role": "user", "content": text},
        ]
        try:
            grok = chat_completion(cfg=ai_cfg, messages=messages, temperature=0.0)
        except XAiError as exc:
            _emit_error(kind="xai_error", message=str(exc), code=1, command="analyze", details={"tweet_id": tid})

        records.append(
            {
                "ok": True,
                "tweet_id": tid,
                "tweet_url": f"https://x.com/i/status/{tid}",
                "text": text,
                "grok": grok,
                "provenance": {
                    "x_api_base_url": x_cfg.base_url,
                    "xai_base_url": ai_cfg.base_url,
                    "model": ai_cfg.model or "grok",
                },
            }
        )

    emit_jsonl(records, out)

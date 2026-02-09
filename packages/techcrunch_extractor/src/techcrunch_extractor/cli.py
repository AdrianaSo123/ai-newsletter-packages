from __future__ import annotations

import json
from pathlib import Path
import typer

from .client import TechCrunchClient
from .fetcher import fetch_rss_items
from .normalizer import normalize_rss_item


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main() -> None:
    """TechCrunch extractor CLI."""
    return


@app.command()
def extract(
    rss_url: str = typer.Option("https://techcrunch.com/feed/", help="RSS feed URL"),
    limit: int = typer.Option(25, min=1, max=200, help="Max items to fetch"),
    out: Path | None = typer.Option(None, help="Write normalized JSONL to this path"),
    user_agent: str | None = typer.Option(None, help="Optional User-Agent"),
) -> None:
    """Fetch TechCrunch RSS and emit normalized JSONL."""
    try:
        with TechCrunchClient(user_agent=user_agent) as client:
            raw_items = fetch_rss_items(client, rss_url=rss_url, limit=limit)
        normalized = [normalize_rss_item(i) for i in raw_items]
    except Exception as exc:
        typer.echo(f"TechCrunch extraction failed: {exc}", err=True)
        raise typer.Exit(code=1)

    if not normalized:
        typer.echo("Warning: fetched 0 RSS items.", err=True)

    lines = [json.dumps(obj.model_dump(mode="json"), ensure_ascii=False) for obj in normalized]
    if out is None:
        for line in lines:
            typer.echo(line)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


@app.command()
def fetch(
    rss_url: str = typer.Option("https://techcrunch.com/feed/", help="RSS feed URL"),
    limit: int = typer.Option(25, min=1, max=200, help="Max items to fetch"),
    out: Path | None = typer.Option(None, help="Write raw RSS-derived JSONL to this path"),
    user_agent: str | None = typer.Option(None, help="Optional User-Agent"),
) -> None:
    """Fetch TechCrunch RSS and emit raw-ish JSONL records."""
    try:
        with TechCrunchClient(user_agent=user_agent) as client:
            raw_items = fetch_rss_items(client, rss_url=rss_url, limit=limit)
    except Exception as exc:
        typer.echo(f"TechCrunch fetch failed: {exc}", err=True)
        raise typer.Exit(code=1)

    if not raw_items:
        typer.echo("Warning: fetched 0 RSS items.", err=True)
    lines = [json.dumps(i.__dict__, ensure_ascii=False) for i in raw_items]
    if out is None:
        for line in lines:
            typer.echo(line)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

from __future__ import annotations

import json
from pathlib import Path
import typer

from .config import RedditAuthConfig, RedditConfigError
from .client import RedditClient
from .fetcher import fetch_new_posts, search_posts
from .io import emit_jsonl, emit_raw_jsonl
from .normalizer import normalize_post
from .oauth import build_authorize_url, exchange_code_for_tokens, generate_state


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
    """Reddit extractor CLI."""
    return


@app.command("auth")
def auth_cmd(
    client_id: str | None = typer.Option(None, help="Reddit app client_id"),
    client_secret: str | None = typer.Option(None, help="Reddit app client_secret"),
    redirect_uri: str = typer.Option(
        "http://localhost:8080",
        help="Redirect URI configured in your Reddit app",
    ),
    scope: str = typer.Option(
        "read identity",
        help="Space-separated OAuth scopes (minimum: read)",
    ),
    state: str | None = typer.Option(None, help="CSRF state (auto-generated if omitted)"),
    code: str | None = typer.Option(None, help="Authorization code from redirect URL"),
) -> None:
    """Help you set up Reddit OAuth.

    1) Run without --code to print the authorize URL.
    2) After authorizing, copy the `code=` value from the redirect URL and run again with --code.
       This prints `REDDIT_REFRESH_TOKEN` you can paste into `.venv/.env`.
    """

    # Load user agent from env (required for Reddit API usage).
    try:
        cfg = RedditAuthConfig.from_env()
    except RedditConfigError as exc:
        _emit_error(kind="config_error", message=str(exc), code=2, command="auth")

    client_id = (client_id or cfg.client_id or "").strip() or None
    client_secret = (client_secret or cfg.client_secret or "").strip() or None

    if not client_id:
        _emit_error(
            kind="config_error",
            message="Missing client_id. Set REDDIT_CLIENT_ID in .venv/.env or pass --client-id.",
            code=2,
            command="auth",
        )
    if not client_secret:
        _emit_error(
            kind="config_error",
            message="Missing client_secret. Set REDDIT_CLIENT_SECRET in .venv/.env or pass --client-secret.",
            code=2,
            command="auth",
        )

    state_val = state or generate_state()
    scopes = [s for s in (scope or "").split() if s.strip()]
    if not scopes:
        scopes = ["read"]

    if not code:
        url = build_authorize_url(
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state_val,
            scope=scopes,
            duration="permanent",
        )
        typer.echo("Open this URL in your browser and approve:")
        typer.echo(url)
        typer.echo("\nAfter redirect, copy the `code` parameter and rerun:")
        typer.echo("  reddit-extractor auth --code <CODE> --state " + state_val)
        raise typer.Exit(code=0)

    token = exchange_code_for_tokens(
        client_id=client_id,
        client_secret=client_secret,
        code=code,
        redirect_uri=redirect_uri,
        user_agent=cfg.user_agent,
    )
    if not token.refresh_token:
        _emit_error(
            kind="auth_error",
            message="No refresh_token returned. Ensure you used duration=permanent and the redirect_uri matches your app settings.",
            code=1,
            command="auth",
        )

    typer.echo("\nPaste these into .venv/.env (do not commit secrets):")
    typer.echo(f"REDDIT_CLIENT_ID=\"{client_id}\"")
    typer.echo(f"REDDIT_CLIENT_SECRET=\"{client_secret}\"")
    typer.echo(f"REDDIT_REFRESH_TOKEN=\"{token.refresh_token}\"")


@app.command("extract")
def extract_cmd(
    subreddit: str = typer.Option(..., help="Subreddit name (no r/ prefix)"),
    query: str | None = typer.Option(None, help="Search query; if omitted uses /new"),
    limit: int = typer.Option(25, min=1, max=100, help="Max posts"),
    sort: str = typer.Option("new", help="Search sort (relevance, hot, top, new, comments)"),
    time_filter: str = typer.Option("month", help="Search time filter (hour, day, week, month, year, all)"),
    out: Path | None = typer.Option(None, help="Write normalized JSONL to this path"),
) -> None:
    """Fetch Reddit posts and emit normalized JSONL."""
    try:
        config = RedditAuthConfig.from_env()
    except RedditConfigError as exc:
        _emit_error(kind="config_error", message=str(exc), code=2, command="extract")

    if not config.has_any_token_source():
        _emit_error(
            kind="config_error",
            message=(
                "Missing Reddit credentials. Set REDDIT_ACCESS_TOKEN or "
                "REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET/REDDIT_REFRESH_TOKEN."
            ),
            code=2,
            command="extract",
        )

    try:
        with RedditClient(config=config) as client:
            if query:
                posts, rl = search_posts(
                    client,
                    subreddit=subreddit,
                    query=query,
                    limit=limit,
                    sort=sort,
                    time_filter=time_filter,
                )
            else:
                posts, rl = fetch_new_posts(client, subreddit=subreddit, limit=limit)
    except Exception as exc:
        _emit_error(kind="api_error", message=str(exc), code=1, command="extract")

    normalized = [normalize_post(p) for p in posts]
    emit_jsonl(normalized, out)

    if rl.used is not None or rl.remaining is not None:
        typer.echo(
            f"rate_limit used={rl.used} remaining={rl.remaining} reset_s={rl.reset_seconds}",
            err=True,
        )


@app.command("fetch")
def fetch_cmd(
    subreddit: str = typer.Option(..., help="Subreddit name (no r/ prefix)"),
    query: str | None = typer.Option(None, help="Search query; if omitted uses /new"),
    limit: int = typer.Option(25, min=1, max=100, help="Max posts"),
    sort: str = typer.Option("new", help="Search sort (relevance, hot, top, new, comments)"),
    time_filter: str = typer.Option("month", help="Search time filter (hour, day, week, month, year, all)"),
    out: Path | None = typer.Option(None, help="Write raw JSONL to this path"),
) -> None:
    """Fetch Reddit posts and emit raw JSONL records."""
    try:
        config = RedditAuthConfig.from_env()
    except RedditConfigError as exc:
        _emit_error(kind="config_error", message=str(exc), code=2, command="fetch")

    if not config.has_any_token_source():
        _emit_error(
            kind="config_error",
            message=(
                "Missing Reddit credentials. Set REDDIT_ACCESS_TOKEN or "
                "REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET/REDDIT_REFRESH_TOKEN."
            ),
            code=2,
            command="fetch",
        )

    try:
        with RedditClient(config=config) as client:
            if query:
                posts, rl = search_posts(
                    client,
                    subreddit=subreddit,
                    query=query,
                    limit=limit,
                    sort=sort,
                    time_filter=time_filter,
                )
            else:
                posts, rl = fetch_new_posts(client, subreddit=subreddit, limit=limit)
    except Exception as exc:
        _emit_error(kind="api_error", message=str(exc), code=1, command="fetch")

    emit_raw_jsonl((p.__dict__ for p in posts), out)

    if rl.used is not None or rl.remaining is not None:
        typer.echo(
            f"rate_limit used={rl.used} remaining={rl.remaining} reset_s={rl.reset_seconds}",
            err=True,
        )

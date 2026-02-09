from __future__ import annotations

import json
from pathlib import Path

import typer

from .extractor import CrunchbaseExtractor
from .domain.errors import CrunchbaseIntelError, FetchError, InvalidInputError


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main() -> None:
    """Crunchbase Intel CLI."""
    return


@app.command("org")
def org_cmd(
    url: str | None = typer.Option(None, help="Crunchbase organization URL (public)", show_default=False),
    html_file: Path | None = typer.Option(None, exists=True, help="Parse from a saved HTML file"),
    min_delay_s: float = typer.Option(1.0, help="Minimum delay between HTTP requests"),
) -> None:
    """Extract a Company record from a Crunchbase organization page.

    Exactly one of --url or --html-file is required.
    """

    if (url is None) == (html_file is None):
        typer.echo("Provide exactly one of --url or --html-file.", err=True)
        raise typer.Exit(code=2)

    extractor = CrunchbaseExtractor(min_delay_s=min_delay_s)

    try:
        if url is not None:
            result = extractor.extract_org_from_url(url)
        else:
            assert html_file is not None
            result = extractor.extract_org_from_html_file(html_file, url=url)
    except CrunchbaseIntelError as exc:
        payload: dict[str, object] = {
            "ok": False,
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        }
        if isinstance(exc, FetchError):
            payload["error"] = {
                **payload["error"],
                "kind": exc.kind,
                "url": exc.url,
                "status_code": exc.status_code,
            }
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        raise typer.Exit(code=2 if isinstance(exc, InvalidInputError) else 1)
    except Exception as exc:
        payload = {
            "ok": False,
            "error": {"type": "UnexpectedError", "message": str(exc)},
        }
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        raise typer.Exit(code=1)

    typer.echo(
        json.dumps({"ok": True, "result": result.model_dump(mode="json")}, ensure_ascii=False, indent=2)
    )

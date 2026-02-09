from __future__ import annotations

from pathlib import Path
import typer

from .config import CrunchbaseConfig, CrunchbaseConfigError
from .client import CrunchbaseClient
from .fetcher import autocomplete as cb_autocomplete
from .fetcher import get_organization, search_funding_rounds
from .io import emit_json, emit_jsonl
from .normalizer import normalize_funding_round_search_result, normalize_organization


app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main() -> None:
    """Crunchbase extractor CLI."""
    return


@app.command("autocomplete")
def autocomplete_cmd(
    query: str = typer.Option(..., help="Query text"),
    collection_ids: str | None = typer.Option(None, help="Comma-separated collection_ids"),
    limit: int = typer.Option(10, min=1, max=25, help="Max suggestions (<=25)"),
) -> None:
    try:
        config = CrunchbaseConfig.from_env()
    except CrunchbaseConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2)

    with CrunchbaseClient(config=config) as client:
        data = cb_autocomplete(client, query=query, collection_ids=collection_ids, limit=limit)
    emit_json(data, out=None)


@app.command("organization")
def organization_cmd(
    permalink: str = typer.Option(..., help="Organization permalink (e.g. 'tesla-motors')"),
    out: Path | None = typer.Option(None, help="Write normalized JSONL to this path"),
) -> None:
    try:
        config = CrunchbaseConfig.from_env()
    except CrunchbaseConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2)

    with CrunchbaseClient(config=config) as client:
        entity = get_organization(
            client,
            entity_id=permalink,
            field_ids=[
                "identifier",
                "short_description",
                "website",
                "founded_on",
                "rank_org_company",
            ],
            card_ids=["raised_funding_rounds"],
        )
    normalized = [normalize_organization(entity)]
    emit_jsonl(normalized, out)


@app.command("funding-rounds")
def funding_rounds_cmd(
    announced_on_gte: str | None = typer.Option(None, help="Filter announced_on >= YYYY-MM-DD (or YYYY)"),
    money_raised_gte: int | None = typer.Option(None, help="Filter money_raised >= value"),
    currency: str = typer.Option("usd", help="Currency code for money_raised predicate"),
    limit: int = typer.Option(100, min=1, max=1000, help="Max results per page (<=1000)"),
    out: Path | None = typer.Option(None, help="Write normalized JSONL to this path"),
) -> None:
    try:
        config = CrunchbaseConfig.from_env()
    except CrunchbaseConfigError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2)

    with CrunchbaseClient(config=config) as client:
        search_resp = search_funding_rounds(
            client,
            announced_on_gte=announced_on_gte,
            money_raised_gte=money_raised_gte,
            currency=currency,
            limit=limit,
        )
    normalized = normalize_funding_round_search_result(search_resp)
    emit_jsonl(normalized, out)


def _emit_jsonl(items, out: Path | None) -> None:
    # Backwards-compatible wrapper; prefer emit_jsonl() directly.
    emit_jsonl(items, out)

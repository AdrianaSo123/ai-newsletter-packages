from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ports import CrunchbaseApi


def autocomplete(
    client: CrunchbaseApi,
    *,
    query: str,
    collection_ids: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    params: dict[str, Any] = {"query": query, "limit": min(limit, 25)}
    if collection_ids:
        params["collection_ids"] = collection_ids
    return client.get("/autocompletes", params=params)


def get_organization(
    client: CrunchbaseApi,
    *,
    entity_id: str,
    field_ids: list[str] | None = None,
    card_ids: list[str] | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if field_ids:
        params["field_ids"] = ",".join(field_ids)
    if card_ids:
        params["card_ids"] = ",".join(card_ids)
    return client.get(f"/entities/organizations/{entity_id}", params=params)


def search_funding_rounds(
    client: CrunchbaseApi,
    *,
    announced_on_gte: str | None,
    money_raised_gte: int | None,
    currency: str = "usd",
    limit: int = 100,
) -> dict[str, Any]:
    query: list[dict[str, Any]] = []
    if announced_on_gte:
        query.append(
            {
                "type": "predicate",
                "field_id": "announced_on",
                "operator_id": "gte",
                "values": [announced_on_gte],
            }
        )
    if money_raised_gte is not None:
        query.append(
            {
                "type": "predicate",
                "field_id": "money_raised",
                "operator_id": "gte",
                "values": [{"value": money_raised_gte, "currency": currency}],
            }
        )

    body = {
        "field_ids": [
            "identifier",
            "announced_on",
            "funded_organization_identifier",
            "money_raised",
            "investment_type",
            "num_investors",
        ],
        "query": query,
        "limit": min(limit, 1000),
        "order": [{"field_id": "announced_on", "sort": "desc"}],
    }
    return client.post("/searches/funding_rounds", json_body=body)

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .types import InvestmentIntelItem


def normalize_organization(entity: dict[str, Any]) -> InvestmentIntelItem:
    data = (entity or {}).get("data") or {}
    props = (data.get("properties") or {})
    identifier = props.get("identifier") or {}

    title = identifier.get("value")
    permalink = identifier.get("permalink")
    url = f"https://www.crunchbase.com/organization/{permalink}" if permalink else None
    summary = props.get("short_description")

    return InvestmentIntelItem(
        source="crunchbase",
        source_record_type="organization",
        source_record_id=permalink or (identifier.get("uuid") if isinstance(identifier, dict) else None),
        url=url,
        title=title,
        summary=summary,
        published_at=None,
        entities=[f"ORG:{title}"] if title else [],
        tags=["company"],
        raw=entity,
    )


def normalize_funding_round_search_result(search_resp: dict[str, Any]) -> list[InvestmentIntelItem]:
    entities = (((search_resp or {}).get("data") or {}).get("entities") or [])
    out: list[InvestmentIntelItem] = []
    for e in entities:
        props = (e.get("properties") or {})
        ident = props.get("identifier") or {}
        fr_name = ident.get("value")
        fr_uuid = ident.get("uuid")
        announced_on = props.get("announced_on")
        published_at = None
        if announced_on:
            try:
                published_at = datetime.fromisoformat(str(announced_on)).replace(tzinfo=timezone.utc)
            except Exception:
                published_at = None

        funded_org = props.get("funded_organization_identifier") or {}
        funded_name = funded_org.get("value")
        funded_permalink = funded_org.get("permalink")
        url = (
            f"https://www.crunchbase.com/organization/{funded_permalink}"
            if funded_permalink
            else None
        )

        money_raised = props.get("money_raised")
        summary = None
        if isinstance(money_raised, dict):
            value = money_raised.get("value")
            currency = money_raised.get("currency")
            if value is not None and currency:
                summary = f"Money raised: {value} {currency}"

        out.append(
            InvestmentIntelItem(
                source="crunchbase",
                source_record_type="funding_round",
                source_record_id=fr_uuid,
                url=url,
                title=(funded_name or fr_name),
                summary=summary,
                published_at=published_at,
                entities=[f"ORG:{funded_name}"] if funded_name else [],
                tags=["funding_round"],
                raw=e,
            )
        )
    return out

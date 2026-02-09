from __future__ import annotations

import re
import uuid
from dataclasses import asdict
from typing import Any

from .models import IntelRecord


def build_kg_bundle(records: list[IntelRecord]) -> dict[str, Any]:
    """Convert extracted intel records into KG-friendly entities + relationships.

    Output is a plain JSON-serializable dict with two lists:
    - entities: each item is a node with an `id`, `entity_type`, and `properties`.
    - relationships: each item is an edge with an `id`, `relationship_type`, `from_id`, `to_id`.
    """

    entities_by_id: dict[str, dict[str, Any]] = {}
    relationships_by_id: dict[str, dict[str, Any]] = {}

    source_id = _id("source", "techcrunch")
    _upsert_entity(
        entities_by_id,
        {
            "id": source_id,
            "entity_type": "Source",
            "properties": {"name": "TechCrunch"},
        },
    )

    for r in records:
        article_id = _id("article", r.article.url)
        _upsert_entity(
            entities_by_id,
            {
                "id": article_id,
                "entity_type": "Article",
                "properties": {
                    "title": r.article.title,
                    "url": r.article.url,
                    "published_at": r.article.published_at.isoformat() if r.article.published_at else None,
                    "author": r.article.author,
                    "categories": list(r.article.categories or []),
                    "guid": r.article.guid,
                    "source": r.article.source,
                },
            },
        )

        company_name = (r.investment.company or "").strip() or None
        if not company_name:
            continue

        company_id = _id("company", _norm_name(company_name))
        _upsert_entity(
            entities_by_id,
            {
                "id": company_id,
                "entity_type": "Company",
                "properties": {"name": company_name},
            },
        )

        # Company -> mentioned_in -> Article
        _upsert_relationship(
            relationships_by_id,
            {
                "id": _id("rel", f"mentioned_in:{company_id}:{article_id}"),
                "relationship_type": "mentioned_in",
                "from_id": company_id,
                "to_id": article_id,
                "properties": {"source": "techcrunch"},
            },
        )

        # Investment entity + required relationship Investment -> reported_by -> Source(TechCrunch)
        investment_key = f"{company_id}:{article_id}:{r.investment.amount_text or ''}:{r.investment.stage or ''}"
        investment_id = _id("investment", investment_key)
        _upsert_entity(
            entities_by_id,
            {
                "id": investment_id,
                "entity_type": "Investment",
                "properties": {
                    "company_id": company_id,
                    "article_id": article_id,
                    "amount_text": r.investment.amount_text,
                    "stage": r.investment.stage,
                    "ai_relevant": bool(r.investment.ai_relevant),
                    "extracted_at": r.extracted_at.isoformat(),
                },
            },
        )

        _upsert_relationship(
            relationships_by_id,
            {
                "id": _id("rel", f"reported_by:{investment_id}:{source_id}"),
                "relationship_type": "reported_by",
                "from_id": investment_id,
                "to_id": source_id,
                "properties": {},
            },
        )

        # Company -> received_investment_from -> Investor
        for inv_name in (r.investment.investors or []):
            inv_name2 = (inv_name or "").strip()
            if not inv_name2:
                continue
            investor_id = _id("investor", _norm_name(inv_name2))
            _upsert_entity(
                entities_by_id,
                {
                    "id": investor_id,
                    "entity_type": "Investor",
                    "properties": {"name": inv_name2},
                },
            )

            _upsert_relationship(
                relationships_by_id,
                {
                    "id": _id("rel", f"received_investment_from:{company_id}:{investor_id}:{article_id}"),
                    "relationship_type": "received_investment_from",
                    "from_id": company_id,
                    "to_id": investor_id,
                    "properties": {"article_id": article_id, "source": "techcrunch"},
                },
            )

    return {
        "entities": list(entities_by_id.values()),
        "relationships": list(relationships_by_id.values()),
    }


def _upsert_entity(store: dict[str, dict[str, Any]], entity: dict[str, Any]) -> None:
    entity_id = str(entity["id"])
    if entity_id in store:
        # Merge properties shallowly (first writer wins for non-null values)
        existing = store[entity_id]
        existing_props = dict(existing.get("properties") or {})
        new_props = dict(entity.get("properties") or {})
        for k, v in new_props.items():
            if k not in existing_props or existing_props[k] is None:
                existing_props[k] = v
        existing["properties"] = existing_props
        return
    store[entity_id] = entity


def _upsert_relationship(store: dict[str, dict[str, Any]], rel: dict[str, Any]) -> None:
    rel_id = str(rel["id"])
    if rel_id in store:
        return
    store[rel_id] = rel


def _id(prefix: str, key: str) -> str:
    # Stable UUID derived from a key; good for later KG merges.
    u = uuid.uuid5(uuid.NAMESPACE_URL, f"techcrunch-intel:{prefix}:{key}")
    return f"{prefix}:{u}"


_NAME_CLEAN_RE = re.compile(r"\s+", re.UNICODE)


def _norm_name(name: str) -> str:
    s = name.strip().lower()
    s = _NAME_CLEAN_RE.sub(" ", s)
    return s

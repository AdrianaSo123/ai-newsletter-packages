from __future__ import annotations

import json
from typing import Any

from bs4 import BeautifulSoup

from ..domain.errors import ParseError
from ..domain.models import Company, UnavailableField


class PublicOrgPageParser:
    """Conservative parser for public Crunchbase organization pages.

    Policy:
    - Extract only from structured markup (JSON-LD) and safe meta tags.
    - Do not infer funding rounds/investors/people roles.
    """

    def parse_company(
        self, html: str, *, url: str | None
    ) -> tuple[Company, list[UnavailableField], dict[str, Any]]:
        try:
            soup = BeautifulSoup(html or "", "html.parser")
        except Exception as exc:
            raise ParseError(f"Failed to initialize HTML parser: {exc}") from exc

        raw: dict[str, Any] = {}
        unavailable: list[UnavailableField] = []

        company = Company(name=None, crunchbase_url=url, description=None, categories=[])

        ld_json = _extract_jsonld(soup)
        if ld_json is not None:
            raw["jsonld"] = ld_json
            company = _apply_jsonld(company, ld_json)

        # Meta fallback for name/description if JSON-LD is absent.
        if company.name is None:
            og_title = _meta(soup, "property", "og:title")
            if og_title:
                company.name = og_title

        if company.description is None:
            og_desc = _meta(soup, "property", "og:description")
            if og_desc:
                company.description = og_desc

        unavailable.extend(
            [
                UnavailableField(
                    field="funding_rounds",
                    reason="Funding rounds are not reliably available from public HTML without paid/API access.",
                ),
                UnavailableField(
                    field="investors",
                    reason="Investor lists are not reliably available from public HTML without paid/API access.",
                ),
                UnavailableField(
                    field="people_roles",
                    reason="People/role data is typically not available without paid/API access.",
                ),
            ]
        )

        if company.name is None:
            unavailable.append(
                UnavailableField(
                    field="company.name",
                    reason=(
                        "Company name not found in structured markup or meta tags "
                        "(page may be blocked or not an org page)."
                    ),
                )
            )

        return company, unavailable, raw


def _extract_jsonld(soup: BeautifulSoup) -> dict[str, Any] | None:
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for s in scripts:
        text = (s.string or s.get_text() or "").strip()
        if not text:
            continue

        try:
            data = json.loads(text)
        except Exception:
            continue

        if isinstance(data, dict):
            if data.get("@type") in ("Organization", "Corporation", "Company"):
                return data

            graph = data.get("@graph")
            if isinstance(graph, list):
                for item in graph:
                    if isinstance(item, dict) and item.get("@type") in (
                        "Organization",
                        "Corporation",
                        "Company",
                    ):
                        return item

            return data

    return None


def _apply_jsonld(company: Company, data: dict[str, Any]) -> Company:
    if not isinstance(data, dict):
        return company

    name = data.get("name")
    url = data.get("url")
    desc = data.get("description")

    if isinstance(name, str) and name.strip():
        company.name = name.strip()
    if isinstance(url, str) and url.strip() and company.crunchbase_url is None:
        company.crunchbase_url = url.strip()
    if isinstance(desc, str) and desc.strip():
        company.description = desc.strip()

    return company


def _meta(soup: BeautifulSoup, attr: str, key: str) -> str | None:
    tag = soup.find("meta", attrs={attr: key})
    if tag is None:
        return None
    val = tag.get("content")
    if not isinstance(val, str):
        return None
    val2 = val.strip()
    return val2 or None

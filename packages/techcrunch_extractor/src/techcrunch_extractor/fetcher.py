from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
import xml.etree.ElementTree as ET

from .client import TechCrunchClient


@dataclass(frozen=True)
class TechCrunchRssItem:
    guid: str | None
    title: str | None
    link: str | None
    description: str | None
    pub_date: str | None
    categories: list[str]
    author: str | None


def fetch_rss_items(
    client: TechCrunchClient,
    *,
    rss_url: str = "https://techcrunch.com/feed/",
    limit: int = 25,
) -> list[TechCrunchRssItem]:
    xml_text = client.get_text(rss_url)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        snippet = (xml_text or "").strip().replace("\n", " ")[:200]
        raise RuntimeError(
            f"Failed to parse RSS XML from {rss_url}. Response may not be RSS. "
            f"Details: {exc}. First chars: {snippet!r}"
        ) from exc

    channel = root.find("channel")
    if channel is None:
        raise RuntimeError(
            f"RSS channel element not found for {rss_url}. Response may not be an RSS feed."
        )

    items: list[TechCrunchRssItem] = []
    for item_el in channel.findall("item"):
        if len(items) >= limit:
            break

        title = _text(item_el, "title")
        link = _text(item_el, "link")
        guid = _text(item_el, "guid")
        description = _text(item_el, "description")
        pub_date = _text(item_el, "pubDate")

        categories = [
            (c.text or "").strip()
            for c in item_el.findall("category")
            if (c.text or "").strip()
        ]

        author = None
        for child in item_el:
            if child.tag.endswith("creator") and (child.text or "").strip():
                author = (child.text or "").strip()
                break

        items.append(
            TechCrunchRssItem(
                guid=guid,
                title=title,
                link=link,
                description=description,
                pub_date=pub_date,
                categories=categories,
                author=author,
            )
        )
    return items


def _text(parent: ET.Element, tag: str) -> str | None:
    el = parent.find(tag)
    if el is None:
        return None
    val = (el.text or "").strip()
    return val or None

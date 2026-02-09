# techcrunch-extractor

TechCrunch RSS extractor and normalizer for investment intelligence.

## What it does

- Fetches TechCrunch RSS feeds (e.g. `https://techcrunch.com/feed/`).
- Emits JSONL records in a small normalized schema (`InvestmentIntelItem`).

## What it can/cannot extract

- Can extract: RSS-provided fields (title, link, published time, categories/tags, short description, GUID, author when present).
- Cannot extract (by design): full article body, paywalled content, or additional page-derived metadata (this package is RSS-only).

## Constraints

- RSS usage is governed by TechCrunch’s RSS Terms of Use; ensure attribution/link-back and comply with their rules.
- Be polite: cache and avoid high-frequency polling.

## Install (isolated)

```bash
cd packages/techcrunch_extractor
python3 -m poetry install
```

## Run

```bash
python3 -m poetry run techcrunch-extractor extract --rss-url https://techcrunch.com/feed/ --limit 25 --out tc.jsonl
```

## Test

```bash
python3 -m poetry run pytest
```

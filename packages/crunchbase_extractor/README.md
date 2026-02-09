# crunchbase-extractor

Crunchbase **paid API** extractor and normalizer for investment intelligence (PoC).

This package uses Crunchbase’s official API and requires an API key (license/plan dependent). If you do **not** have paid API access, use `crunchbase-intel` instead (public web/snapshots, explicit “unavailable” on blocked access).

## Install

```bash
cd packages/crunchbase_extractor
python3 -m poetry install
```

## Configure

```bash
export CRUNCHBASE_USER_KEY="..."
```

## Examples

```bash
python3 -m poetry run crunchbase-extractor autocomplete --query "airbnb" --collection-ids organization.companies --limit 5
python3 -m poetry run crunchbase-extractor organization --permalink tesla-motors --out tesla.jsonl
python3 -m poetry run crunchbase-extractor funding-rounds --announced-on-gte 2025-01-01 --money-raised-gte 10000000 --currency usd --limit 100 --out rounds.jsonl
```

## Test

```bash
python3 -m poetry run pytest
```

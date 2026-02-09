# crunchbase-extractor

Crunchbase **paid API** extractor and normalizer for investment intelligence (PoC).

This package uses Crunchbase’s official API and requires an API key (license/plan dependent). If you do **not** have paid API access, use `crunchbase-intel` instead (public web/snapshots, explicit “unavailable” on blocked access).

## Install

```bash
python3 -m pip install -e packages/crunchbase_extractor
```

## Configure

```bash
export CRUNCHBASE_USER_KEY="..."
```

## Examples

```bash
crunchbase-extractor autocomplete --query "airbnb" --collection-ids organization.companies --limit 5
crunchbase-extractor organization --permalink tesla-motors --out tesla.jsonl
crunchbase-extractor funding-rounds --announced-on-gte 2025-01-01 --money-raised-gte 10000000 --currency usd --limit 100 --out rounds.jsonl
```

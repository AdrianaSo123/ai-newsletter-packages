# techcrunch-intel

Educational / demonstration package that ingests **TechCrunch RSS** and produces **structured metadata + best-effort investment signals** for AI-related startup funding news.

## What it does

- Fetches recent TechCrunch RSS entries (default: `https://techcrunch.com/feed/`).
- Filters for **AI** + **investment/funding** related content.
- Extracts lightweight structured signals (best-effort): company, amount, stage, investors.
- Outputs structured Python objects and/or JSON via `techcrunch_intel.export`.

## Data source & compliance

- Primary ingestion method: TechCrunch RSS feeds.
- This package is intended for **research/education**.
- It does **not** redistribute TechCrunch article bodies; it focuses on derived metadata/signals.
- If you enable optional HTML fetching, do so sparingly and respect TechCrunch RSS terms and site terms.

## Install (Poetry)

```bash
cd techcrunch_intel
poetry install
```

## Example usage

```python
from techcrunch_intel.ingest import fetch_rss_entries
from techcrunch_intel.pipeline import build_intel_records

entries = fetch_rss_entries("https://techcrunch.com/feed/", limit=25)
records = build_intel_records(entries)

for r in records:
    print(r.article.title, r.investment.amount_text, r.investment.stage)
```

To export JSONL:

```python
from pathlib import Path
from techcrunch_intel.export import export_jsonl

export_jsonl(records, Path("out.jsonl"))
```

## KG-ready output

To emit **knowledge-graph-friendly JSON** (entities + relationships), use:

```python
from pathlib import Path
from techcrunch_intel.export import export_kg_json
from techcrunch_intel.kg import build_kg_bundle

bundle = build_kg_bundle(records)
export_kg_json(bundle, Path("kg.json"))
```

The `kg.json` file contains:

- `entities`: `Company`, `Investor`, `Article`, `Investment`, and a `Source` entity for `TechCrunch`.
- `relationships` (minimum set):
    - `Company -> received_investment_from -> Investor`
    - `Company -> mentioned_in -> Article`
    - `Investment -> reported_by -> Source(TechCrunch)`


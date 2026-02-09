from __future__ import annotations

from pathlib import Path

import httpx

from techcrunch_intel.export import export_jsonl, export_kg_json
from techcrunch_intel.ingest import fetch_rss_entries
from techcrunch_intel.kg import build_kg_bundle
from techcrunch_intel.pipeline import build_intel_records


def main() -> int:
    rss = "https://techcrunch.com/feed/"
    ua = "techcrunch-intel/0.1 (educational)"

    resp = httpx.get(rss, headers={"User-Agent": ua}, timeout=30.0)
    print("RSS HTTP:", resp.status_code)
    print("RSS bytes:", len(resp.content))
    print("RSS content-type:", resp.headers.get("content-type"))
    print("RSS date:", resp.headers.get("date"))

    entries = fetch_rss_entries(rss, limit=50)
    print("\nFetched entries:", len(entries))
    for a in entries[:5]:
        print("-", a.title)
        print(" ", a.url)

    records = build_intel_records(entries)
    print("\nEmitted records:", len(records))
    for r in records[:5]:
        print("-", r.article.title)
        print(
            "  company=",
            r.investment.company,
            "amount=",
            r.investment.amount_text,
            "ai_relevant=",
            r.investment.ai_relevant,
            "notes=",
            r.investment.notes,
        )

    out_dir = Path("tmp")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_jsonl = out_dir / "techcrunch_intel_real.jsonl"
    export_jsonl(records, out_jsonl)
    print("\nWrote JSONL:", out_jsonl.resolve())

    bundle = build_kg_bundle(records)
    out_kg = out_dir / "techcrunch_intel_real_kg.json"
    export_kg_json(bundle, out_kg)
    print("Wrote KG JSON:", out_kg.resolve())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

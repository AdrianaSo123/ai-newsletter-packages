from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Any

from .models import IntelRecord


def export_kg_json(bundle: dict[str, Any], path: Path) -> None:
        """Write a KG-ready bundle to a single JSON file.

        Bundle shape:
        {
            "entities": [ ... ],
            "relationships": [ ... ]
        }
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_json(records: Iterable[IntelRecord]) -> str:
    payload = [r.to_dict() for r in records]
    return json.dumps(payload, ensure_ascii=False, indent=2)


def export_jsonl(records: Iterable[IntelRecord], path: Path) -> None:
    lines = [json.dumps(r.to_dict(), ensure_ascii=False) for r in records]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


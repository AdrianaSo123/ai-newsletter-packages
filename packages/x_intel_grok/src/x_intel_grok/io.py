from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def emit_jsonl(records: Iterable[dict], out: Path | None) -> None:
    lines = [json.dumps(r, ensure_ascii=False) for r in records]
    if out is None:
        for line in lines:
            print(line)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

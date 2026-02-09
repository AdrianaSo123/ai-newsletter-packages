from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel


def emit_json(payload: object, out: Path | None) -> None:
    encoded = json.dumps(payload, ensure_ascii=False)
    if out is None:
        print(encoded)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(encoded + "\n", encoding="utf-8")


def emit_jsonl(models: Iterable[BaseModel], out: Path | None) -> None:
    lines = [json.dumps(m.model_dump(mode="json"), ensure_ascii=False) for m in models]
    if out is None:
        for line in lines:
            print(line)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

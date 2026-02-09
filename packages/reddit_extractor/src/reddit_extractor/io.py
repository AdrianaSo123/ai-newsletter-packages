from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from pydantic import BaseModel


def emit_jsonl(models: Iterable[BaseModel], out: Path | None) -> None:
    lines = [json.dumps(m.model_dump(mode="json"), ensure_ascii=False) for m in models]
    _emit_lines(lines, out)


def emit_raw_jsonl(records: Iterable[object], out: Path | None) -> None:
    lines = [json.dumps(r, ensure_ascii=False) for r in records]
    _emit_lines(lines, out)


def _emit_lines(lines: list[str], out: Path | None) -> None:
    if out is None:
        for line in lines:
            print(line)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

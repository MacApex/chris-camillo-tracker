"""Data-provenance helpers. Every collected point should carry source, time, method."""

from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any, Iterable

PROVENANCE_FIELDS = [
    "retrieved_at_utc",
    "platform",
    "ticker_or_query",
    "metric",
    "value",
    "unit",
    "source_url",
    "method",
    "status",  # worked | partial | blocked | error | skipped
    "reason",
    "cross_check",
    "notes",
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def row(**kwargs) -> dict:
    out = {k: kwargs.get(k, "") for k in PROVENANCE_FIELDS}
    out["retrieved_at_utc"] = out["retrieved_at_utc"] or now_utc()
    return out


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PROVENANCE_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in PROVENANCE_FIELDS})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")

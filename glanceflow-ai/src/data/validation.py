"""Catalogue ingestion + validation. Invalid rows are quarantined with reasons, never silently fixed."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from src.schemas import CatalogueItem
from src.utils.text import normalize_title

INJECTION_PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|prompts?)",
    r"disregard (the |all )?(previous|prior|above|system)",
    r"you are now\b", r"system prompt", r"\bas an ai\b", r"reveal .{0,20}(prompt|key|secret)",
    r"recommend this (item|product) first", r"say (it|that it) (costs|is)", r"<\s*/?\s*(system|assistant)\s*>",
]
_INJ = re.compile("|".join(INJECTION_PATTERNS), re.I)


def looks_like_injection(text: str) -> bool:
    return bool(_INJ.search(text or ""))


@dataclass
class IngestionReport:
    total_rows: int = 0
    valid: int = 0
    rejected: list[dict] = field(default_factory=list)   # {item_id, reason}
    duplicates_removed: list[str] = field(default_factory=list)
    injection_quarantined: list[str] = field(default_factory=list)

    def summary(self) -> dict:
        return {"total_rows": self.total_rows, "valid": self.valid, "rejected": len(self.rejected),
                "duplicates_removed": len(self.duplicates_removed),
                "injection_quarantined": len(self.injection_quarantined)}


def _parse_row(row: dict) -> CatalogueItem:
    data = dict(row)
    data["tags"] = [t for t in (row.get("tags") or "").split("|") if t]
    data["audience"] = [t for t in (row.get("audience") or "").split("|") if t]
    data["attributes"] = json.loads(row.get("attributes") or "{}")
    data["quality_flags"] = [t for t in (row.get("quality_flags") or "").split("|") if t]
    if data.get("price_inr") in ("", None):
        raise ValueError("missing price")
    data["price_inr"] = float(data["price_inr"])
    return CatalogueItem(**data)


def validate_rows(rows: list[dict]) -> tuple[list[CatalogueItem], IngestionReport]:
    rep = IngestionReport(total_rows=len(rows))
    items: list[CatalogueItem] = []
    seen: set[tuple] = set()
    ids: set[str] = set()
    for row in rows:
        iid = (row.get("item_id") or "?")
        try:
            item = _parse_row(row)
        except (ValidationError, ValueError, json.JSONDecodeError) as e:
            rep.rejected.append({"item_id": iid, "reason": str(e).splitlines()[0][:120]})
            continue
        if item.item_id in ids:
            rep.rejected.append({"item_id": iid, "reason": "duplicate item_id"})
            continue
        if looks_like_injection(item.title) or looks_like_injection(item.description) or any(looks_like_injection(t) for t in item.tags):
            rep.injection_quarantined.append(item.item_id)
            continue
        key = (normalize_title(item.title), item.category, round(item.price_inr))
        if key in seen:
            rep.duplicates_removed.append(item.item_id)
            continue
        seen.add(key)
        ids.add(item.item_id)
        items.append(item)
    rep.valid = len(items)
    return items, rep


def load_catalogue(path: Path) -> tuple[list[CatalogueItem], IngestionReport]:
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return validate_rows(rows)

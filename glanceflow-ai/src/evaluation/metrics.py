from __future__ import annotations

import statistics

from src.schemas import CatalogueItem
from src.utils.text import tokenize


def violates(item: CatalogueItem, q: dict) -> list[str]:
    v = []
    if q.get("oracle_budget_max") is not None and item.price_inr > q["oracle_budget_max"]:
        v.append("over_budget")
    if item.availability == "out_of_stock":
        v.append("out_of_stock")
    if q["oracle_exclusions"] and set(q["oracle_exclusions"]) & set(tokenize(" ".join([item.title, item.subcategory, *item.tags]))):
        v.append("excluded_term")
    return v


def is_relevant(item: CatalogueItem, q: dict) -> bool:
    return not violates(item, q) and bool(set(q["expected_interests"]) & {t.lower() for t in item.tags})


def summarize(rows: list[dict]) -> dict:
    """rows: per-query dicts with returned items, latency, etc."""
    n = len(rows)
    returned = sum(r["n_returned"] for r in rows)
    return {
        "queries": n,
        "precision_at_5": round(statistics.mean(r["relevant"] / 5 for r in rows), 3) if n else None,
        "precision_of_returned": round(sum(r["relevant"] for r in rows) / returned, 3) if returned else None,
        "hit_rate_at_5": round(sum(1 for r in rows if r["relevant"] > 0) / n, 3) if n else None,
        "constraint_violation_rate": round(sum(r["violations"] for r in rows) / returned, 3) if returned else None,
        "queries_with_any_violation": sum(1 for r in rows if r["violations"] > 0),
        "avg_returned": round(returned / n, 2) if n else None,
        "avg_distinct_subcategories": round(statistics.mean(r["distinct_sub"] for r in rows), 2) if n else None,
        "avg_distinct_base_products": round(statistics.mean(r["distinct_base"] for r in rows), 2) if n else None,
        "zero_result_rate": round(sum(1 for r in rows if r["n_returned"] == 0) / n, 3) if n else None,
        "median_latency_ms": round(statistics.median(r["latency_ms"] for r in rows), 2) if n else None,
    }

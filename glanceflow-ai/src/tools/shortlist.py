from __future__ import annotations

from src.retrieval.ranking import budget_status
from src.schemas import CatalogueItem, Constraints


def comparison_table(items: list[CatalogueItem], fit_reasons: dict[str, str] | None = None, c: Constraints | None = None) -> list[dict]:
    """Consistent criteria for every item; values come only from catalogue fields."""
    fit_reasons = fit_reasons or {}
    rows = []
    for it in items:
        rows.append({
            "Item": it.title, "ID": it.item_id, "Category": it.category, "Price (₹)": int(it.price_inr),
            "Availability": it.availability.replace("_", " "),
            "Practical": "Yes" if it.attributes.get("practical") else "No",
            "Handmade": "Yes" if it.attributes.get("handmade") else "No",
            "Eco-friendly": "Yes" if it.attributes.get("eco_friendly") else "No",
            "Generic gift item": "Yes" if it.attributes.get("generic_gift") else "No",
            "Budget": budget_status(it, c) if c else "n/a",
            "Why it fits": fit_reasons.get(it.item_id, ""),
        })
    return rows

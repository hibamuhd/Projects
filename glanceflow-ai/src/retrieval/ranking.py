"""Transparent scoring. Hard constraints are applied BEFORE this module (see tools/catalogue_search.py);
here only soft preferences move items up or down."""
from __future__ import annotations

import statistics
from collections import Counter

from src.schemas import Candidate, CatalogueItem, Constraints, RankedItem

WEIGHTS = {"relevance": 0.30, "interest": 0.30, "preference": 0.15, "budget_fit": 0.10, "personalization": 0.05}
GENERIC_PENALTY = 0.25


def budget_status(item: CatalogueItem, c: Constraints) -> str:
    if c.budget_max is None and c.budget_min is None:
        return "no budget set"
    if c.budget_max is not None and item.price_inr > c.budget_max:
        return "over budget"
    if c.budget_min is not None and item.price_inr < c.budget_min:
        return "under minimum"
    if c.budget_max is not None:
        return f"within budget (₹{int(c.budget_max - item.price_inr):,} to spare)"
    return "within range"


def _pref_hits(item: CatalogueItem, prefs: list[str], p75: float) -> list[str]:
    a = item.attributes
    hits = []
    for p in prefs:
        ok = {
            "practical": bool(a.get("practical")),
            "unique": bool(a.get("handmade")) or not a.get("generic_gift", False),
            "eco_friendly": bool(a.get("eco_friendly")),
            "handmade": bool(a.get("handmade")),
            "premium": bool(a.get("premium")) or item.price_inr >= p75,
        }.get(p, False)
        if ok:
            hits.append(p)
    return hits


def score_candidates(cands: list[Candidate], c: Constraints, profile: dict | None = None) -> list[RankedItem]:
    if not cands:
        return []
    profile = profile or {}
    saved: Counter = profile.get("saved_categories", Counter())
    dismissed: Counter = profile.get("dismissed_categories", Counter())
    max_rel = max(x.retrieval_score for x in cands) or 1.0
    prices = sorted(x.item.price_inr for x in cands)
    p75 = prices[int(0.75 * (len(prices) - 1))]
    out: list[RankedItem] = []
    for cd in cands:
        it = cd.item
        rel = cd.retrieval_score / max_rel
        matched = [i for i in c.interests if i in {t.lower() for t in it.tags}]
        interest = (len(matched) / len(c.interests)) if c.interests else 0.0
        hits = _pref_hits(it, c.preferred_attributes, p75)
        pref = (len(hits) / len(c.preferred_attributes)) if c.preferred_attributes else 0.0
        if c.budget_max:
            ratio = it.price_inr / c.budget_max
            bfit = 1.0 if 0.35 <= ratio <= 1.0 else 0.6 + ratio
        else:
            bfit = 0.5
        pers = 0.0
        if saved.get(it.category):
            pers += min(1.0, 0.5 * saved[it.category])
        if dismissed.get(it.category):
            pers -= min(1.0, 0.5 * dismissed[it.category])
        pers = max(-1.0, min(1.0, pers))
        comps = {"relevance": rel, "interest": interest, "preference": pref, "budget_fit": min(1.0, bfit), "personalization": pers}
        score = sum(WEIGHTS[k] * v for k, v in comps.items())
        generic_hit = c.avoid_generic and bool(it.attributes.get("generic_gift"))
        if generic_hit:
            score -= GENERIC_PENALTY
        comps["generic_penalty"] = -GENERIC_PENALTY if generic_hit else 0.0
        reasons: list[str] = []
        if matched:
            reasons.append("Matches interest: " + ", ".join(matched))
        for h in hits:
            reasons.append({"practical": "Practical, everyday use", "unique": "Less generic than typical gift items",
                            "eco_friendly": "Eco-friendly", "handmade": "Handmade", "premium": "Premium tier"}[h])
        if c.avoid_generic and not generic_hit and "unique" not in hits:
            reasons.append("Not flagged as a generic gift item")
        reasons.append(f"₹{int(it.price_inr):,} - {budget_status(it, c)}")
        if saved.get(it.category):
            reasons.append(f"You saved other {it.category} items")
        out.append(RankedItem(item=it, score=round(score, 4), components={k: round(v, 4) for k, v in comps.items()},
                              reasons=reasons, budget_status=budget_status(it, c)))
    out.sort(key=lambda r: (-r.score, r.item.item_id))
    return out


def select_diverse(ranked: list[RankedItem], n: int, per_subcategory: int = 2, per_category: int = 3) -> list[RankedItem]:
    """Greedy diversity-aware selection; caps relax only if not enough items would otherwise be returned."""
    for sub_cap, cat_cap, base_cap in ((per_subcategory, per_category, 1), (per_subcategory + 1, per_category + 1, 2), (n, n, n)):
        picked: list[RankedItem] = []
        sub, cat, base = Counter(), Counter(), Counter()
        for r in ranked:
            b = r.item.attributes.get("base_name", r.item.title)
            if sub[r.item.subcategory] >= sub_cap or cat[r.item.category] >= cat_cap or base[b] >= base_cap:
                continue
            picked.append(r); sub[r.item.subcategory] += 1; cat[r.item.category] += 1; base[b] += 1
            if len(picked) == n:
                return picked
        if len(picked) == min(n, len(ranked)):
            return picked
    return ranked[:n]

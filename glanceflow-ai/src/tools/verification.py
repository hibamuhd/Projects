"""Deterministic verification. The catalogue is the single source of truth for price/availability/attributes."""
from __future__ import annotations

import re

from src.data.validation import looks_like_injection
from src.schemas import CatalogueItem, Constraints, RankedItem, VerificationIssue, VerificationReport
from src.utils.text import normalize_title, tokenize

_RUPEE = re.compile(r"(?:₹|rs\.?\s*)\s*([\d,]+(?:\.\d+)?)", re.I)


def check_item(r: RankedItem, c: Constraints, truth: dict[str, CatalogueItem], min_score: float) -> list[VerificationIssue]:
    it, iss = r.item, []
    real = truth.get(it.item_id)
    if real is None:
        return [VerificationIssue(code="unknown_item_id", item_id=it.item_id, message="Item ID is not in the catalogue (possible hallucination).")]
    if real.price_inr != it.price_inr or real.title != it.title or real.availability != it.availability:
        iss.append(VerificationIssue(code="catalogue_mismatch", item_id=it.item_id, message="Item facts differ from the catalogue record."))
    if c.budget_max is not None and real.price_inr > c.budget_max:
        iss.append(VerificationIssue(code="over_budget", item_id=it.item_id, message=f"₹{int(real.price_inr):,} exceeds maximum ₹{int(c.budget_max):,}."))
    if c.budget_min is not None and real.price_inr < c.budget_min:
        iss.append(VerificationIssue(code="under_minimum", item_id=it.item_id, message="Below the stated minimum budget."))
    if real.availability == "out_of_stock":
        iss.append(VerificationIssue(code="out_of_stock", item_id=it.item_id, message="Item is out of stock."))
    if c.category and real.category != c.category:
        iss.append(VerificationIssue(code="wrong_category", item_id=it.item_id, message="Outside the selected category."))
    if c.exclusions and set(c.exclusions) & set(tokenize(" ".join([real.title, real.subcategory, *real.tags]))):
        iss.append(VerificationIssue(code="excluded_term", item_id=it.item_id, message="Contains a term the user excluded."))
    if looks_like_injection(real.title) or looks_like_injection(real.description):
        iss.append(VerificationIssue(code="prompt_injection", item_id=it.item_id, message="Catalogue text failed the safety screen."))
    if r.score < min_score:
        iss.append(VerificationIssue(code="weak_relevance", item_id=it.item_id, message=f"Score {r.score:.2f} below floor {min_score:.2f}.", severity="soft"))
    return iss


def verify_recommendations(ranked: list[RankedItem], c: Constraints, truth: dict[str, CatalogueItem], min_score: float,
                           min_results: int, audit_only: bool = False) -> tuple[list[RankedItem], VerificationReport]:
    issues: list[VerificationIssue] = []
    seen_ids, seen_keys = set(), set()
    kept: list[RankedItem] = []
    removed: list[str] = []
    for r in ranked:
        item_issues = check_item(r, c, truth, min_score)
        key = (normalize_title(r.item.title), round(r.item.price_inr))
        if r.item.item_id in seen_ids or key in seen_keys:
            item_issues.append(VerificationIssue(code="duplicate", item_id=r.item.item_id, message="Duplicate of another result."))
        issues += item_issues
        if any(i.severity == "hard" for i in item_issues) and not audit_only:
            removed.append(r.item.item_id)
            continue
        seen_ids.add(r.item.item_id); seen_keys.add(key)
        kept.append(r)
    hard = [i for i in issues if i.severity == "hard"]
    if len(kept) < min_results and not audit_only:
        issues.append(VerificationIssue(code="too_few_results", message=f"Only {len(kept)} verified results (need {min_results}).", severity="soft"))
    rep = VerificationReport(passed=not hard and len(kept) >= min_results, issues=issues, checked_count=len(ranked),
                             removed_ids=removed, needs_revision=(len(kept) < min_results) and not audit_only, audit_only=audit_only)
    return kept, rep


def explanation_is_grounded(text: str, item: CatalogueItem, c: Constraints) -> bool:
    """Any rupee amount in generated text must equal the item's price or the user's budget bounds; no injection phrases."""
    allowed = {int(item.price_inr)} | {int(x) for x in (c.budget_max, c.budget_min) if x is not None}
    for m in _RUPEE.finditer(text):
        if int(float(m.group(1).replace(",", ""))) not in allowed:
            return False
    return not looks_like_injection(text) and len(text) <= 400

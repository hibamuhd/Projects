"""Discovery tools: hard filtering, retrieval, de-duplication. All deterministic."""
from __future__ import annotations

from dataclasses import dataclass, field

from src.data.validation import looks_like_injection
from src.retrieval.index import Retriever
from src.schemas import Candidate, CatalogueItem, Constraints
from src.utils.text import normalize_title, tokenize

RELATED = {"reading": ["writing", "study", "stationery"], "coffee": ["tea", "kitchen"], "tea": ["coffee", "wellness"],
           "cooking": ["kitchen", "baking"], "baking": ["cooking"], "fitness": ["wellness", "yoga"], "yoga": ["wellness", "fitness"],
           "tech": ["study"], "art": ["craft", "games"], "travel": ["tech"], "games": ["puzzle", "art"], "home": ["plants"],
           "wellness": ["home"], "study": ["stationery", "reading"], "writing": ["stationery"], "learning": ["study"],
           "music": ["tech"], "fashion": ["travel"], "plants": ["home"], "snacks": ["cooking"], "stationery": ["study", "writing"]}


def hard_filter(items: list[CatalogueItem], c: Constraints, excluded_ids: set[str] | frozenset[str] = frozenset()) -> list[CatalogueItem]:
    """Hard constraints: availability, budget range, explicit category, exclusions, dismissed items."""
    excl = set(c.exclusions)
    out = []
    for it in items:
        if it.item_id in excluded_ids or it.availability == "out_of_stock":
            continue
        if looks_like_injection(it.title) or looks_like_injection(it.description):  # layer 2 of 3 (ingestion, discovery, critic)
            continue
        if c.budget_max is not None and it.price_inr > c.budget_max:
            continue
        if c.budget_min is not None and it.price_inr < c.budget_min:
            continue
        if c.category and it.category != c.category:
            continue
        if excl and excl & set(tokenize(" ".join([it.title, it.subcategory, *it.tags]))):
            continue
        out.append(it)
    return out


def dedupe(items: list[CatalogueItem]) -> tuple[list[CatalogueItem], list[str]]:
    seen, out, dropped = set(), [], []
    for it in items:
        k = (normalize_title(it.title), round(it.price_inr))
        if it.item_id in {x.item_id for x in out} or k in seen:
            dropped.append(it.item_id)
            continue
        seen.add(k)
        out.append(it)
    return out, dropped


def build_query_tokens(c: Constraints, relax: int = 0) -> list[str]:
    toks = list(c.interests) + list(c.keywords)
    if not c.interests and not c.keywords and c.category:
        toks += tokenize(c.category)
    if relax >= 1:
        for i in c.interests:
            toks += RELATED.get(i, [])
    return tokenize(" ".join(toks))


@dataclass
class SearchOutput:
    candidates: list[Candidate]
    pool_size: int
    dropped_duplicates: list[str] = field(default_factory=list)
    query_tokens: list[str] = field(default_factory=list)


def search_catalogue(retriever: Retriever, catalogue: list[CatalogueItem], c: Constraints, k: int = 40,
                     relax: int = 0, excluded_ids: set[str] | frozenset[str] = frozenset()) -> SearchOutput:
    pool = hard_filter(catalogue, c, excluded_ids)
    tokens = build_query_tokens(c, relax)
    by_id = {i.item_id: i for i in pool}
    hits = retriever.search(tokens, allowed_ids=set(by_id), k=k) if tokens else []
    items, dropped = dedupe([by_id[i] for i, _ in hits])
    keep = {i.item_id for i in items}
    cands = [Candidate(item=by_id[i], retrieval_score=s) for i, s in hits if i in keep]
    return SearchOutput(cands, len(pool), dropped, tokens)


def keyword_baseline(retriever: Retriever, catalogue: list[CatalogueItem], raw_query: str, k: int = 5) -> list[Candidate]:
    """Control arm: plain keyword retrieval on the raw query. No budget/availability/exclusion handling."""
    by_id = {i.item_id: i for i in catalogue}
    hits = retriever.search(tokenize(raw_query), None, k=k)
    return [Candidate(item=by_id[i], retrieval_score=s) for i, s in hits]

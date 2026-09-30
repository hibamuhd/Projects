"""Agent B - Discovery. Tool-driven candidate generation from the local catalogue."""
from __future__ import annotations

from src.retrieval.index import Retriever
from src.schemas import CatalogueItem, Constraints
from src.tools.catalogue_search import SearchOutput, keyword_baseline, search_catalogue


class DiscoveryAgent:
    def __init__(self, retriever: Retriever, catalogue: list[CatalogueItem]):
        self.retriever, self.catalogue = retriever, catalogue

    def run(self, c: Constraints, relax: int = 0, excluded_ids: set[str] | frozenset[str] = frozenset(), k: int = 40) -> SearchOutput:
        return search_catalogue(self.retriever, self.catalogue, c, k=k, relax=relax, excluded_ids=excluded_ids)

    def run_baseline(self, raw_query: str, k: int = 5) -> SearchOutput:
        cands = keyword_baseline(self.retriever, self.catalogue, raw_query, k)
        return SearchOutput(cands, len(self.catalogue))

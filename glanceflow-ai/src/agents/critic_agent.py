"""Agent D - Critic & Verification. Purely deterministic checks against the catalogue as ground truth."""
from __future__ import annotations

from src.schemas import CatalogueItem, Constraints, RankedItem, VerificationReport
from src.tools.verification import verify_recommendations


class CriticAgent:
    def __init__(self, catalogue: list[CatalogueItem], min_score: float, min_results: int):
        self.truth = {i.item_id: i for i in catalogue}
        self.min_score, self.min_results = min_score, min_results

    def run(self, ranked: list[RankedItem], c: Constraints, audit_only: bool = False) -> tuple[list[RankedItem], VerificationReport]:
        return verify_recommendations(ranked, c, self.truth, self.min_score, self.min_results, audit_only)

from __future__ import annotations

from src.schemas import Constraints
from src.storage.repositories import PreferenceRepo


def remember_explicit(repo: PreferenceRepo, c: Constraints) -> dict:
    """Stores only what the user explicitly stated in their latest request (visible in Settings)."""
    prefs = {"budget_max": c.budget_max, "interests": c.interests, "exclusions": c.exclusions,
             "preferred_attributes": c.preferred_attributes, "avoid_generic": c.avoid_generic}
    for k, v in prefs.items():
        repo.set(k, v)
    return prefs

"""Seeded demo events so the analytics dashboard has something to render on a fresh install.
Every row is flagged is_seeded=1 and properties.origin='seeded_demo'. Probabilities below are ARBITRARY demo values,
identical across experiment arms on purpose: they demonstrate dashboard mechanics and imply NO product effect."""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone

from src.schemas import CatalogueItem
from src.tools.analytics import EventLogger

ORIGIN = {"origin": "seeded_demo"}


def seed_demo_events(logger: EventLogger, catalogue: list[CatalogueItem], n_sessions: int = 60, seed: int = 11) -> int:
    rng = random.Random(seed)
    base = datetime.now(timezone.utc) - timedelta(days=6)
    n = 0

    def ev(t, sid, ref=None, props=None, when=None):
        nonlocal n
        n += 1
        logger.log(t, sid, ref, {**(props or {}), **ORIGIN}, is_seeded=True, ts=(when or base).isoformat(timespec="milliseconds"))

    for k in range(n_sessions):
        sid = f"demo-{uuid.UUID(int=rng.getrandbits(128)).hex[:10]}"
        t = base + timedelta(minutes=rng.randint(0, 8000))
        arm = rng.choice(["treatment", "control"])
        ev("session_started", sid, when=t)
        if rng.random() < 0.9:
            rid = f"demo-run-{k}"
            has_budget = rng.random() < 0.7
            ev("query_submitted", sid, rid, {"is_refinement": False}, t)
            if rng.random() < 0.08:
                ev("clarification_requested", sid, rid, {}, t)
                continue
            ok = rng.random() < 0.95
            n_res = rng.randint(3, 5) if ok else 0
            verif_fail = rng.random() < 0.1
            ev("results_generated", sid, rid, {"status": "ok" if ok else "no_results", "n_results": n_res, "has_budget": has_budget,
                                               "latency_ms": round(rng.lognormvariate(1.0, 0.4), 2), "retrieval_arm": arm, "card_arm": arm,
                                               "pre_verification_violations": 0, "final_violations": 0, "revisions": int(verif_fail),
                                               "est_cost_usd": None}, t)
            if verif_fail:
                ev("agent_verification_failed", sid, rid, {"codes": ["too_few_results"]}, t)
            if not ok:
                continue
            picks = rng.sample(catalogue, n_res)
            for it in picks:
                ev("recommendation_viewed", sid, it.item_id, {}, t)
            if rng.random() < 0.3:
                ev("query_refined", sid, f"{rid}-r", {}, t)
            saved_any = False
            for it in picks:
                if rng.random() < 0.22:
                    ev("recommendation_saved", sid, it.item_id, {"category": it.category}, t)
                    ev("action_completed", sid, it.item_id, {"action": "save"}, t)
                    saved_any = True
                elif rng.random() < 0.08:
                    ev("feedback_submitted", sid, it.item_id, {"reason": rng.choice(["irrelevant", "too_expensive", "not_my_style", "already_have", "other"])}, t)
            if not saved_any and rng.random() < 0.15:
                ev("comparison_started", sid, None, {"n_items": 2}, t)
                ev("action_completed", sid, None, {"action": "compare"}, t)
    return n

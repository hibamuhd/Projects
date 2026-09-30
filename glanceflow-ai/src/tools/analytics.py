"""Event logging + deterministic analytics computed from recorded events.
Descriptive only: nothing here supports causal claims."""
from __future__ import annotations

import statistics
from collections import Counter, defaultdict

from src.storage.database import Database, PersistenceError
from src.storage.repositories import EventRepo
from src.utils.logging_config import get_logger

log = get_logger("analytics")

EVENT_TYPES = {
    "session_started", "query_submitted", "clarification_requested", "results_generated", "recommendation_viewed",
    "recommendation_saved", "comparison_started", "recommendation_dismissed", "feedback_submitted", "query_refined",
    "action_completed", "agent_verification_failed", "experiment_exposure",
}


class EventLogger:
    """Never raises: analytics failures must not break the user journey (and are logged, not hidden)."""
    def __init__(self, db: Database):
        self.repo = EventRepo(db)
        self.failures = 0

    def log(self, event_type: str, session_id: str, ref_id: str | None = None, properties: dict | None = None,
            is_seeded: bool = False, ts: str | None = None) -> str | None:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unknown event type {event_type}")
        try:
            return self.repo.add(session_id, event_type, ref_id, properties, is_seeded, ts)
        except PersistenceError as e:
            self.failures += 1
            log.warning("event %s not recorded: %s", event_type, e)
            return None


def _pct(a: int, b: int) -> float | None:
    return round(100 * a / b, 1) if b else None


def _p95(xs: list[float]) -> float | None:
    if len(xs) < 20:
        return None  # not enough samples for a stable p95
    xs = sorted(xs)
    return round(xs[int(0.95 * (len(xs) - 1))], 1)


def compute_metrics(events: list[dict]) -> dict:
    """Metric definitions (numerator / denominator) are documented in docs/METRICS.md."""
    by_type: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        by_type[e["event_type"]].append(e)
    sessions = {e["session_id"] for e in by_type["session_started"]}
    results = by_type["results_generated"]
    queries = by_type["query_submitted"]
    ok_results = [e for e in results if e["properties"].get("n_results", 0) > 0 and e["properties"].get("status") in ("ok", "fallback")]
    sess_with_results = {e["session_id"] for e in results}
    viewed = {(e["session_id"], e["ref_id"]) for e in by_type["recommendation_viewed"]}
    saved = {(e["session_id"], e["ref_id"]) for e in by_type["recommendation_saved"]}
    completed_sessions = {e["session_id"] for e in by_type["action_completed"] if e["properties"].get("action") in ("save", "compare")}
    lat = [float(e["properties"]["latency_ms"]) for e in results if "latency_ms" in e["properties"]]
    verif_failed_queries = {e["ref_id"] for e in by_type["agent_verification_failed"]}
    costs = [e["properties"].get("est_cost_usd") for e in results]
    priced = [c for c in costs if c is not None]
    final_viol = sum(e["properties"].get("final_violations", 0) for e in results)
    pre_viol = sum(e["properties"].get("pre_verification_violations", 0) for e in results)
    recs_total = sum(e["properties"].get("n_results", 0) for e in results)
    fb = Counter(e["properties"].get("reason", "unknown") for e in by_type["feedback_submitted"])
    n_completed = len(completed_sessions & sess_with_results)
    seg: dict[str, dict] = {}
    for key in ("retrieval_arm", "has_budget", "card_arm"):
        groups: dict[str, list[dict]] = defaultdict(list)
        for e in results:
            groups[str(e["properties"].get(key, "n/a"))].append(e)
        seg[key] = {}
        for g, evs in groups.items():
            sids = {e["session_id"] for e in evs}
            g_viewed = {(e["session_id"], e["ref_id"]) for e in by_type["recommendation_viewed"] if e["session_id"] in sids}
            g_saved = {(e["session_id"], e["ref_id"]) for e in by_type["recommendation_saved"] if e["session_id"] in sids}
            seg[key][g] = {"queries_with_results": len(evs), "save_rate_pct": _pct(len(g_saved & g_viewed), len(g_viewed)),
                           "violation_rate_pct": _pct(sum(e["properties"].get("pre_verification_violations", 0) for e in evs),
                                                      sum(e["properties"].get("n_results", 0) for e in evs))}
    return {
        "counts": {"sessions": len(sessions), "queries": len(queries), "results_events": len(results), "events_total": len(events),
                   "seeded_events": sum(1 for e in events if e.get("is_seeded")), "live_events": sum(1 for e in events if not e.get("is_seeded"))},
        "activation_rate_pct": _pct(len(sess_with_results & sessions), len(sessions)),
        "search_to_results_success_pct": _pct(len(ok_results), len(queries)),
        "save_rate_pct": _pct(len(saved & viewed), len(viewed)),
        "refinement_rate_pct": _pct(len(by_type["query_refined"]), len(results)),
        "task_completion_rate_pct": _pct(n_completed, len(sess_with_results)),
        "latency_median_ms": round(statistics.median(lat), 1) if lat else None,
        "latency_p95_ms": _p95(lat),
        "latency_n": len(lat),
        "verification_failure_rate_pct": _pct(len(verif_failed_queries), len(results)),
        "est_cost_per_completed_task_usd": round(sum(priced) / n_completed, 6) if priced and n_completed else None,
        "constraint_violation_rate_pct": _pct(final_viol, recs_total),
        "pre_verification_violation_rate_pct": _pct(pre_viol, recs_total),
        "feedback_distribution": dict(fb),
        "funnel": [("Sessions", len(sessions)), ("Submitted a query", len({e["session_id"] for e in queries})),
                   ("Got results", len(sess_with_results)), ("Viewed a recommendation", len({s for s, _ in viewed})),
                   ("Saved or compared", len(completed_sessions & sess_with_results))],
        "segments": seg,
    }

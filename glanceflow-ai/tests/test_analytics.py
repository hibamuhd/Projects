from src.tools.analytics import EventLogger, compute_metrics
from src.storage.repositories import EventRepo
import pytest


def test_empty_dataset_does_not_crash():  # scenario 17
    m = compute_metrics([])
    assert m["counts"]["events_total"] == 0 and m["activation_rate_pct"] is None
    assert m["latency_median_ms"] is None and m["latency_p95_ms"] is None and m["funnel"][0] == ("Sessions", 0)


def _ev(t, s, ref=None, **p):
    return {"event_type": t, "session_id": s, "ref_id": ref, "properties": p, "is_seeded": 0}


def test_funnel_and_rates_from_events():
    evs = [_ev("session_started", "a"), _ev("session_started", "b"),
           _ev("query_submitted", "a", "r1"), _ev("results_generated", "a", "r1", n_results=3, status="ok", latency_ms=10, pre_verification_violations=0, final_violations=0),
           _ev("recommendation_viewed", "a", "i1"), _ev("recommendation_viewed", "a", "i2"),
           _ev("recommendation_saved", "a", "i1"), _ev("action_completed", "a", "i1", action="save"),
           _ev("query_refined", "a", "r2")]
    m = compute_metrics(evs)
    assert m["activation_rate_pct"] == 50.0 and m["save_rate_pct"] == 50.0 and m["task_completion_rate_pct"] == 100.0
    assert m["refinement_rate_pct"] == 100.0 and m["search_to_results_success_pct"] == 100.0
    assert [n for _, n in m["funnel"]] == [2, 1, 1, 1, 1]


def test_p95_needs_enough_samples_and_cost_needs_pricing():
    few = [_ev("results_generated", "a", str(i), n_results=1, status="ok", latency_ms=float(i)) for i in range(5)]
    m = compute_metrics(few)
    assert m["latency_median_ms"] == 2.0 and m["latency_p95_ms"] is None and m["est_cost_per_completed_task_usd"] is None
    many = [_ev("results_generated", "a", str(i), n_results=1, status="ok", latency_ms=float(i)) for i in range(40)]
    assert compute_metrics(many)["latency_p95_ms"] is not None


def test_verification_failure_and_violation_rates():
    evs = [_ev("results_generated", "a", "r1", n_results=5, status="ok", pre_verification_violations=2, final_violations=0),
           _ev("results_generated", "a", "r2", n_results=5, status="ok", pre_verification_violations=0, final_violations=0),
           _ev("agent_verification_failed", "a", "r1")]
    m = compute_metrics(evs)
    assert m["verification_failure_rate_pct"] == 50.0 and m["pre_verification_violation_rate_pct"] == 20.0 and m["constraint_violation_rate_pct"] == 0.0


def test_seeded_vs_live_are_distinguishable(db):
    log = EventLogger(db)
    log.log("session_started", "x", is_seeded=True)
    log.log("session_started", "y")
    m = compute_metrics(EventRepo(db).all())
    assert m["counts"]["seeded_events"] == 1 and m["counts"]["live_events"] == 1
    assert compute_metrics(EventRepo(db).all(include_seeded=False))["counts"]["sessions"] == 1


def test_unknown_event_type_rejected(db):
    with pytest.raises(ValueError):
        EventLogger(db).log("made_up_event", "s")


def test_event_has_required_fields(db):
    EventLogger(db).log("session_started", "s1", "ref", {"k": "v"})
    e = EventRepo(db).all()[0]
    assert e["event_id"] and e["ts"] and e["session_id"] == "s1" and e["event_type"] == "session_started" and e["properties"] == {"k": "v"}

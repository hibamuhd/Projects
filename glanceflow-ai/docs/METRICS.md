# Metrics

All computed by `src/tools/analytics.py::compute_metrics` from recorded events. Window: all events in the selected view (Live only, or Live + seeded demo); no rolling window is implemented. All are **descriptive**; none supports a causal claim.

| Metric | Numerator | Denominator | Limitations |
|---|---|---|---|
| Activation rate | sessions with ≥1 `results_generated` | `session_started` sessions | a session that only got a clarification counts as not activated |
| Search-to-results success | queries whose results event has ≥1 result and status ok/fallback | `query_submitted` | refinements count as queries; clarifications lower it |
| Recommendation save rate | unique (session, item) saved | unique (session, item) viewed | "viewed" = returned to UI (impression), not scrolled-into-view |
| Refinement rate | `query_refined` events | `results_generated` events | a refinement can signal engagement or dissatisfaction; not separable here |
| Session task-completion | sessions with a save or compare `action_completed` (and results) | sessions with results | saving is a proxy for intent, not purchase |
| Latency p50 / p95 | median / 95th percentile of `latency_ms` on results events | — | p95 shown only with ≥20 samples; excludes UI time; sandbox hardware |
| Verification failure rate | queries with ≥1 `agent_verification_failed` | `results_generated` | in the control arm the critic runs in audit-only mode, so failures = violations found |
| Est. cost per completed task | sum of priced `est_cost_usd` | completed sessions | `None` unless per-token prices are configured; deterministic mode has no LLM cost |
| Constraint-violation rate (final) | shown recommendations failing a hard check | shown recommendations | should be 0 by construction in treatment |
| Constraint-violation rate (pre-verification) | hard issues found before removal | recommendations returned | the measure that actually differentiates control vs treatment |
| Feedback distribution | count per reason | — | small samples; self-selected |
| Segments | by retrieval arm, card arm, has_budget | — | descriptive; unequal group sizes; seeded data has no built-in arm effect |

**North star (proposed):** satisfied discovery sessions = sessions with results in which the user saved/compared ≥1 item and did not mark every shown item irrelevant. The dashboard's task-completion metric is the first half of this.

Seeded demo events (`is_seeded=1`, `origin=seeded_demo`) use arbitrary probabilities, identical across arms, purely to exercise the dashboard.

# Resume bullets

Every number below was measured in this repo (offline, synthetic catalogue of 283 items, 23 answerable benchmark queries, top-5) unless it is a `[PLACEHOLDER]`. Do not present these as real-user or production results. Keep the "(synthetic, offline)" qualifier.

## A. Product Management-focused
- Identified that keyword-only discovery ignores budget and intent; defined a PRD, ICE-prioritised MVP, north-star metric and two A/B designs, then shipped a working prototype whose offline benchmark cut budget/stock/exclusion violations from 44.3% to 0% and lifted precision@5 from 0.44 to 0.97 (synthetic, offline).
- Scoped out purchases and real integrations to protect trust and delivery; built save/compare/shortlist as the measurable "next action" and instrumented 13 event types for funnel analysis.
- Wrote an experiment plan (session-level randomisation, guardrails, ~1,093 sessions/arm for +5pp on an assumed 20% baseline) instead of claiming impact; real user validation: `[PLACEHOLDER: pilot results]`.

## B. AI / Technical Product Management-focused
- Designed a six-role agent system (intent, discovery, ranking, critic, action, analytics) on an explicit state machine with typed Pydantic contracts, bounded retries/timeouts, a one-revision cap, and an inspectable execution trace; kept filtering, arithmetic, permissions and verification deterministic.
- Made LLM output non-authoritative: extracted budgets must appear in the user's text and generated explanations may only cite catalogue prices, with a documented no-API-key fallback; covered by 80 passing automated tests including hallucinated IDs, injection text, timeouts, retry exhaustion and failed persistence.
- Ran an ablation (keyword vs keyword + hard filters vs full pipeline) showing most of the violation reduction came from constraint filtering, while ranking added +0.235 precision@5 and 1.6 more distinct products per top-5 (synthetic, offline). Live-LLM latency/cost: `[PLACEHOLDER: not measured]`.

## C. Product Analytics-focused
- Built an event pipeline (12 required + 1 exposure event types, SQLite) and derived funnel, activation, save, refinement, completion, p50/p95 latency, verification-failure, violation and cost-per-task metrics from recorded events, each documented with numerator, denominator and limitations.
- Separated seeded demo events from live interactions in schema and dashboard to prevent fabricated conversion claims; designed p95 to display only with ≥20 samples.
- Designed an offline evaluation harness (30 fixed queries, 3 systems) and two A/B experiments with guardrails and sample-size logic; production KPIs: `[PLACEHOLDER: needs real traffic]`.

# Case study — GlanceFlow AI

**Labels used throughout:** *Implemented* (exists in the repo) · *Offline-measured* (benchmark on synthetic data) · *Simulated* (seeded demo events) · *Hypothesis* (needs real users).

## 1. Why the problem matters
Consumer discovery on mobile is a firehose. If users can't get from "I need a gift for X under ₹Y" to a trustworthy shortlist quickly, they abandon or settle for generic picks. *Hypothesis:* this friction is large for students and young professionals. I have no data on its size.

## 2. Assumptions needing validation
People phrase needs in natural language; budget and "not generic" are common constraints; explanations increase trust; a shortlist/compare step is a meaningful "next action". None are validated.

## 3. Target user and JTBD
Digitally active students/young professionals. "When I need a gift within a budget, help me get a short list I trust." (hypothetical personas in the PRD.)

## 4. Journey and pain points
Today (assumed): keyword search → scroll → filter → open many → doubt → repeat. Pain: intent is lost, budget applied late, no "why".

## 5. MVP decisions and trade-offs
Prioritised by impact × confidence ÷ effort (judgement, not data). In: verification, intent parsing with clarification, transparent ranking, save/compare, events. Out: purchases, real integrations, accounts, embeddings. Trade-off: I chose a *verifiably correct* small system over a wide, demo-only one.

## 6. Why agentic AI here
The job splits into steps with different needs: language understanding (fuzzy), retrieval (structured), ranking (judgement + evidence), checking (must be exact), acting (must be safe). Separating them makes each testable and lets the risky parts be deterministic.

## 7. What stays deterministic
Filtering, arithmetic, permissions, persistence, verification, analytics. The LLM is optional and only extracts constraints and phrases one sentence; both outputs are checked against ground truth. *Implemented.*

## 8. Architecture and responsibilities
Six roles (intent, discovery, ranking, critic, action, analytics) over an explicit state machine with a trace. See SYSTEM_ARCHITECTURE. Analytics is a tool, not an agent, by design.

## 9. Ranking and retrieval
BM25 over weighted fields → hard filters → transparent weighted score (relevance, interest match, preference match, budget fit, evidence-only personalization, generic penalty) → diversity caps. Weights are untuned judgement calls.

## 10. Failure cases and safeguards
Conflicts → one clarification question; vague → one question; no match → honest empty state; purchase → refusal; injection → 3-layer screen; LLM failure → deterministic fallback; DB failure → explicit failure, never fake success; loops → ≤1 revision + step cap. *Each tested.*

## 11. Metrics
North star: satisfied discovery sessions. Supporting: activation, search-to-results, save rate, refinement, completion, latency, verification failures, violations, cost per completed task. Definitions in METRICS.

## 12. Offline evaluation *(offline-measured, synthetic)*
23 queries: precision@5 0.443 (keyword) → 0.739 (+hard filters) → 0.974 (full); violation rate 44.3% → 0% → 0%; distinct base products 2.39 → 2.61 → 4.22; edge cases 7/7. The biggest lesson: **most of the trust gain came from applying constraints, not from smarter ranking**. Caveat: labels are tag-derived and partly circular.

## 13. Experiment design *(designed, not run)*
Exp 1 retrieval baseline vs intent-aware; Exp 2 generic vs reasoned cards. Session-level randomisation, exposure logging, guardrails, sample sizes (~1,093/arm to detect +5pp on a 20% baseline — an illustrative assumption). See EXPERIMENT_PLAN.

## 14. What didn't work and what changed
Conflict detection missed "bookworm, no books"; housewarming returned nothing; ranges without ₹ weren't parsed; top-5 lists were near-duplicates. Each was found by the benchmark or tests and fixed (EVALUATION_REPORT §"What went wrong").

## 15. Limitations
Synthetic data, circular labels, rule-based English parsing, untested live LLM, no real users, no browser visual check. See LIMITATIONS.

## 16. Before launching to real users
Real catalogue + partner data contracts; real user research and an A/A then A/B test; semantic retrieval and learned ranking; auth, consent, retention policy, encryption; abuse/rate limiting; a stronger injection defence; cost and latency budgets on real traffic; legal/brand review (no implied affiliation).

## Simulated vs measured vs implemented (summary)
- *Implemented:* everything in the README feature list.
- *Offline-measured:* benchmark table above; 80 passing tests.
- *Simulated:* seeded dashboard events (arbitrary probabilities; no effect built in).
- *Hypotheses:* all user-value claims.

# PRD — GlanceFlow AI (prototype)

Evidence labels: **[Assumption]** believed but unverified · **[Synthetic]** observed only in this repo's synthetic data or offline tests · **[Observed]** verified from a cited source. No customer interviews, user research or production results exist for this project, so nothing below is marked *Observed* about users.

## 1. Problem statement
Digitally active students and young professionals discover products, gifts and lifestyle content on mobile. **[Assumption]** They hit information overload, generic and repetitive recommendations, irrelevant search results, and friction narrowing options (budget, taste, dislikes). Evidence to gather before launch: search reformulation rates, zero-result and abandon rates, interview themes.

## 2. Personas (hypothetical, for design only)
- **Aarav, 21, college student** — gifting on a tight budget, wants practical, non-generic options fast.
- **Meera, 26, young professional** — time-poor, buys for friends/family, wants to trust that a pick is in budget and in stock.

## 3. Jobs to be done
"When I need a gift/item for a specific person and budget, I want a short, trustworthy list that fits, so I can decide without scrolling endless results."

## 4. Current journey and pain points **[Assumption]**
Search keyword → scroll → filter by price → open many items → doubt fit → repeat. Pain: keyword search ignores intent ("not generic"), budget is applied late or not at all, no explanation of *why*.

## 5. Solution and value proposition
Understand intent → retrieve from catalogue → rank transparently → verify constraints deterministically → explain from facts → help with the next action (save/compare/refine). Value: fewer steps to a trustworthy shortlist.

## 6. Requirements
**Functional:** NL request; structured constraints; clarification when materially ambiguous; retrieval + hard filters; ranking with reasons; verification; refine; save/compare/dismiss/feedback; persistence; event tracking; analytics; offline benchmark; deterministic fallback without LLM.
**Non-functional:** correctness of hard constraints (must be 0 violations in shown results); local-first privacy; median request latency well under 1 s in deterministic mode **[Synthetic: measured single-digit ms in a sandbox]**; bounded cost (LLM optional, cost recorded only when pricing is configured); reliability (no crash on LLM/DB failure).

## 7. MVP scope
In: everything above. **Explicit exclusions:** purchases/payments, real catalogue or partner integrations, accounts/auth, real images, embeddings, multi-user analytics, content feed ranking.

## 8. Prioritisation (ICE: Impact/Confidence/Effort, 1–5; score = I×C/E)
| Feature | I | C | E | Score | Why in MVP |
|---|---|---|---|---|---|
| Hard-constraint verification | 5 | 5 | 2 | 12.5 | trust is the core promise; cheap to build deterministically |
| Intent parsing + clarification | 5 | 4 | 3 | 6.7 | enables everything else |
| Transparent ranking + reasons | 4 | 4 | 3 | 5.3 | tests the explanation hypothesis |
| Save/compare/shortlist | 4 | 4 | 2 | 8.0 | gives a measurable "next action" |
| Event analytics | 4 | 5 | 2 | 10.0 | required to learn anything |
| Embedding retrieval | 3 | 2 | 4 | 1.5 | deferred; baseline first |
| Purchases | 3 | 1 | 5 | 0.6 | out of scope; risk high |
Scores are my judgement, not data.

## 9. Primary journey and edge cases
Primary: request → results → save/compare → refine. Edge cases (all handled and tested): no budget, conflicting constraints, vague request, no matches, budget below all prices, out-of-stock items, duplicates, bad catalogue rows, injected catalogue text, purchase request, LLM down, DB down, repeated save, mid-session preference change.

## 10. Hypotheses and experiments
H1: intent-aware ranking beats keyword retrieval on save rate per result-viewing session. H2: "why it fits" text beats generic descriptions on save rate. Designs in [EXPERIMENT_PLAN](EXPERIMENT_PLAN.md).

## 11. Metrics
**North star:** *satisfied discovery sessions* — share of sessions with results in which the user saved or compared ≥1 item and did not flag every shown item as irrelevant. (The prototype computes the save/compare part as "task completion"; feedback-aware refinement is future work.) Supporting: activation, search-to-results success, save rate, refinement rate, verification failure rate, constraint-violation rate, latency p50/p95, estimated cost per completed task. Definitions: [METRICS](METRICS.md).

## 12. Privacy, trust, latency, reliability, cost
Local storage; opt-in external LLM; no raw prompts in events; reset button; grounded explanations only; timeouts + bounded retries + fallbacks; cost tracked only with configured pricing. See [SAFETY_AND_PRIVACY](SAFETY_AND_PRIVACY.md).

## 13. Success criteria and limitations
Prototype success = acceptance criteria in the build brief, met and verified (see EVALUATION_REPORT). Real success would need a real-user test. Limits: [LIMITATIONS](LIMITATIONS.md).

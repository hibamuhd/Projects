# Interview prep (grounded in this repo)

Measured facts you can cite (synthetic, offline): violation rate 44.3% → 0%; precision@5 0.443 → 0.739 → 0.974 across keyword / +filters / full; distinct base products in top-5 2.39 → 4.22; 7/7 edge cases; 80 tests passed. Always add "synthetic catalogue, author-written queries, tag-derived labels".

## 60-second pitch
"I built an independent prototype of agentic discovery: you describe a need like a gift under ₹1,500 for a reader who hates generic things, and it turns that into constraints, retrieves from a synthetic catalogue, ranks with a transparent score, verifies budget and stock in code, explains each pick, and lets you save and compare. The key decision was to use language models only where language is fuzzy and keep everything that must be correct deterministic. Offline on synthetic data, constraint violations dropped from 44% to 0%, but I'm clear that's not real-world proof — I've designed the A/B tests I'd run next."

## 3-minute product walkthrough
Follow docs/DEMO_SCRIPT.md: problem and hypothesis → example query → constraint chips and reasons → save/compare → refine ("cheaper", "actually cooking") → guardrails (purchase refusal, conflict clarification, empty state) → agent activity → analytics with seeded vs live → trust settings. End with what you'd validate first.

## 5-minute architecture
UI → workflow state machine → agents (intent, discovery, ranking, critic; action separate; analytics a tool) → BM25 index + SQLite. Explain: hard constraints filter before scoring; scoring weights (0.30 relevance, 0.30 interest, 0.15 preference, 0.10 budget fit, 0.05 evidence-only personalization, −0.25 generic penalty); critic re-verifies against the catalogue as ground truth and can trigger one revision; transitions are enforced and capped; LLM optional, validated, with fallback; trace shown in the UI; events → metrics.

## Why agents, not one LLM call?
Different steps need different guarantees: parsing tolerates ambiguity, verification tolerates none. Splitting lets me test each, swap retrieval, and insert a critic that can't be talked out of a budget. It also makes failures inspectable (the trace). A single call would blur "guess" and "fact".

## Why not agents for every step?
Filtering, arithmetic, permissions, persistence and analytics are exact; an LLM there adds cost, latency and risk. In the repo, only intent extraction and one-sentence explanations may use an LLM, and both are checked.

## Handling hallucinations
Item IDs looked up in the catalogue; price/title/availability compared to the record; extracted budgets must appear in the user's text; explanation amounts must equal the item price or user budget, else fall back to a template; injected catalogue text is screened three times. Honest gap: regex screens miss novel attacks.

## Evaluating recommendation quality
Offline: fixed queries, precision@k, hit rate, violation rate, diversity, ablations (my B vs C). Online: save/compare rate, "irrelevant" feedback, refinement patterns, then A/B. Weakness of mine: labels come from the same tags the ranker uses, so I'd add human-labelled relevance and pairwise preference tests.

## North-star metric
"Satisfied discovery sessions": sessions with results where the user saved/compared ≥1 item and didn't reject everything. It should represent value delivered (a decision-ready shortlist), not activity. My dashboard implements the save/compare half.

## Measuring retention and relevance
Retention: D1/D7/D28 return rate for users with ≥1 satisfied session — needs accounts, which the prototype lacks. Relevance: save-per-view, negative feedback rate, refinement-after-results (interpret carefully: could be engagement or dissatisfaction), and human-graded samples.

## Running an A/B test
See EXPERIMENT_PLAN: A/A first; session-level randomisation via hash; log exposure at assignment; primary metric save-or-compare rate; guardrails (violations, latency, zero-result, cost); fixed horizon; sample size ~1,093/arm for +5pp on an assumed 20% baseline; watch novelty, query-mix drift and cross-arm contamination.

## Reducing latency and cost
Already: deterministic mode is single-digit ms in the sandbox; LLM off by default. Next: cache constraint extraction, use a small model for extraction, template explanations by default and LLM only for top-1, batch explanations in one call, precomputed embeddings, timeouts/retries capped. I have not measured live-LLM latency or cost.

## Cold-start personalization
Prototype: no evidence → personalization weight is 0 and the feed says "not personalised yet"; explicit statements are stored visibly; only saves/dismissals change ranking. At scale: onboarding taste questions, popularity priors by segment, exploration slots, gradual blend into learned ranking.

## 10,000 or 1 million users
10k: move SQLite→Postgres, add auth, queue analytics writes, cache the index. 1M: embedding retrieval with ANN, feature store, learned ranker with offline replay, event streaming, regional caching, cost budgets per request, monitoring for drift and abuse, stronger moderation of catalogue text.

## Prioritising the next feature
ICE with evidence: first instrument and run an A/A + Exp 1 on real traffic; likely next: embedding retrieval (if zero-result or vocabulary-mismatch rates are high), human-labelled evaluation set, then learned ranking. Purchases only after trust metrics hold.

## What failed and what I learned
The benchmark exposed a missed conflict ("bookworm, no books"), a zero-result query (housewarming), unparsed ranges, and near-duplicate top-5 lists; I fixed each. Two of my own tests encoded wrong expectations. Biggest lesson: ablation showed filtering, not fancy ranking, produced most of the trust gain — so prioritise correctness of constraints before model sophistication.

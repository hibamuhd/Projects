# Evaluation report

Reproduce: `python3 scripts/generate_data.py && python3 scripts/run_evaluation.py` (deterministic, LLM-free; writes `docs/evaluation_results.json`).

## Setup
283 valid synthetic items; 30 fixed queries: 23 answerable + 7 edge cases. Three systems, top 5 each:
- **A** keyword BM25 on the raw query, no constraint handling.
- **B** same retrieval, but with the parsed hard filters (budget, stock, exclusions) applied — isolates the value of *ranking/intent* from the value of *filtering*.
- **C** the full workflow (intent → discover → rank → verify → explain).

Relevance = item passes the hand-written oracle constraints (`oracle_budget_max`, exclusions, in stock) **and** shares ≥1 expected interest tag. Violation = over oracle budget, out of stock, or excluded term.

## Measured results (23 answerable queries)
| Metric | A | B | C |
|---|---|---|---|
| Precision@5 (relevant/5) | 0.443 | 0.739 | 0.974 |
| Precision of returned items | 0.443 | 0.739 | 0.991 |
| Hit rate@5 | 0.783 | 0.913 | 1.000 |
| Constraint-violation rate | 0.443 | 0.000 | 0.000 |
| Queries with any violation | 21/23 | 0/23 | 0/23 |
| Avg items returned | 5.00 | 5.00 | 4.91 |
| Avg distinct subcategories | 1.83 | 2.04 | 3.26 |
| Avg distinct base products | 2.39 | 2.61 | 4.22 |
| Zero-result rate | 0 | 0 | 0 |
| Median latency (sandbox) | ~0.5 ms | ~5.5 ms | ~8.4 ms |

Edge cases (clarify, refuse, no-match): **7/7** handled as expected.

## How to read this
- **Filtering explains most of the violation gap** (A → B). Ranking/intent then adds precision and diversity (B → C: +0.235 precision@5, +1.6 distinct base products).
- **These numbers are optimistic.** Labels come from the same tags the ranker's interest score uses (partly circular), the queries were written by the author, and the catalogue is small and synthetic. C's near-perfect precision shows the pipeline is internally coherent, not that users would prefer it.
- Latency figures are from a single-core sandbox and are only useful as "no obvious bottleneck".
- C returns 4.91 items on average because it never pads with constraint-violating results.

## Automated tests (executed)
`python3 -m pytest` → **80 passed**: intent (13), retrieval/ingestion (8), ranking (5), verification (9), orchestration (16), actions (10), analytics (7), failure modes (9), UI journeys via Streamlit AppTest (3). The Streamlit server was also started and answered HTTP 200 on `/_stcore/health` and `/`.
Coverage of the 18 required scenarios: all 18 have at least one test (mapped by `# scenario N` comments in `tests/`).

## What went wrong during development (real)
1. First benchmark run: edge-case accuracy 6/7 — a "no books" + "bookworm" request wasn't flagged as conflicting because exclusions and interests use different vocabularies. Fixed by mapping excluded words through the interest lexicon.
2. "Housewarming gift under ₹800" returned zero results (no interest keyword). Fixed by treating housewarming as a `home` interest, with an explicit assumption note.
3. "500-1000" wasn't parsed as a range without a currency sign; fixed the regex, ignoring small numbers like "3-4 days".
4. Top-5 lists were dominated by variants of one product (e.g., three "reading journals"); added a base-product diversity cap.
5. Two tests I wrote first failed because they encoded wrong expectations (the injected item is now screened *earlier* than the critic; "buy a gift" wasn't matched by my purchase regex). I fixed the code/tests deliberately and kept both layers.

## Not verified
Live LLM calls; real browser rendering/mobile layout; screenshots; behaviour with real users or a real catalogue; performance at scale.

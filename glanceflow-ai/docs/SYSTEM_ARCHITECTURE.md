# System architecture

## Layers
`app.py` → `src/ui/*` (render only) → `src/orchestration/workflow.py` (state machine) → `src/agents/*` → `src/tools/*` + `src/retrieval/*` → `src/storage/*`.

## Agents (each has distinct capability, typed I/O)
| Agent | Input → Output | Deterministic? | Failure handling |
|---|---|---|---|
| A Intent (`intent_agent.py`) | text, UI filters → `IntentResult` (`Constraints`, clarification question, conflicts, assumptions, unsupported action) | Rules by default; optional LLM extractor | LLM timeout/invalid JSON/ungrounded values → falls back to rules (`source=rules_fallback`) |
| B Discovery (`discovery_agent.py`, `tools/catalogue_search.py`) | `Constraints` → candidates with IDs | Yes (hard filter + BM25 + dedupe) | empty pool → one relaxed revision, else empty state |
| C Ranking (`ranking_agent.py`, `retrieval/ranking.py`) | candidates + interaction profile → scored, diverse top-N with reasons | Yes; LLM only optionally rewrites explanation | LLM text rejected unless grounded → template |
| D Critic (`critic_agent.py`, `tools/verification.py`) | ranked items → kept items + `VerificationReport` | Yes | removes hard violators; requests ≤1 revision; fallback |
| E Action (`action_agent.py`) | `ActionRequest` → `ActionResult` | Yes | invalid/unknown/unauthorised/persist-fail → explicit failure |
| F Analytics (`tools/analytics.py`) | events → metrics | Yes (a tool, not an agent) | empty data → `None` values |

## Scoring (transparent)
`score = 0.30·relevance + 0.30·interest + 0.15·preference + 0.10·budget_fit + 0.05·personalization − 0.25·[avoid_generic ∧ generic item]`. Weights are my judgement (in `retrieval/ranking.py`); they are untuned. Hard constraints (budget, stock, exclusions, category filter, dismissed items) are applied **before** scoring, never traded off. Personalization uses only saved/dismissed categories (evidence), else 0. Diversity: ≤1 per base product, ≤2 per subcategory, ≤3 per category in the first pass; caps relax only if too few items.

## Determinism boundaries
Deterministic: filtering, arithmetic, budget checks, permissions, persistence, verification, analytics. LLM (optional): request → constraint extraction; one-sentence explanation. Both are validated against ground truth.

## Control flow
`WorkflowState.go()` enforces the transition table; `StepLimitExceeded` and `InvalidTransition` are converted to a safe `error` result — never a fabricated success. Every stage appends a `TraceStep` (stage, tool, status, ms, summary) shown in **Agent activity**. No chain-of-thought is stored or shown.

## Retries, timeouts, cost
`call_with_retry` (thread + timeout, bounded attempts, optional output validation) wraps every LLM call. `CostTracker` counts tokens and returns cost **only if** per-million-token prices are configured, else `None`.

## Experiment arms
Control = raw-query keyword BM25 with verification in **audit-only** mode (measures violations, removes nothing) and generic description text. Treatment = full pipeline and reasoned text. `assign()` hashes session ID; Settings can force an arm.

## Storage
SQLite tables: `events`, `shortlist`, `dismissals`, `feedback`, `preferences`. One short-lived connection per operation. Event logging never raises; failures are counted and logged.

## Design decisions
- No LangChain/agent framework: explicit Python + Pydantic is easier to inspect and test.
- Retriever is a `Protocol`; swapping in embeddings needs one new class.
- Impressions (`recommendation_viewed`) are logged when results are returned to the UI, not on scroll — a documented approximation.

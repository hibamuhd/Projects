# Experiment plan

Implemented: deterministic session-level assignment (`src/evaluation/experiment.py`), exposure logging (`experiment_exposure` event), arm-aware UI, arm-tagged result events, offline benchmark. **Not done:** any live A/B run. Offline results are not evidence of real-world impact.

## Experiment 1 — keyword baseline vs intent-aware ranking
- **Hypothesis:** intent-aware ranking raises save rate per session with results and removes constraint violations.
- **Control:** BM25 on the raw query, top 5, no constraint handling (critic audit-only). **Treatment:** full pipeline.
- **Eligible:** sessions that submit a discovery query (not purchase-only, not clarification-only).
- **Randomisation unit:** session (stable hash); consider user ID once accounts exist.
- **Primary metric:** save-or-compare rate per session with results.
- **Guardrails:** constraint-violation rate (must not rise), zero-result rate, p95 latency, no-result/error rate, "irrelevant" feedback share.
- **Sample size:** for baseline 20% and absolute lift +5pp, ~1,093 sessions per arm (α=0.05, power 0.8, two-proportion normal approximation; `required_sample_per_arm`). +3pp needs ~2,940; baseline is unknown and must be measured first.
- **Exposure logging:** log at assignment time, before results render; analyse only exposed sessions.
- **Stopping:** fixed horizon set in advance (no peeking-based stopping); stop early only for a guardrail breach (violations > 0 in treatment, error rate spike).
- **Confounders:** novelty effects; query mix drift by day; bots; catalogue changes mid-test; users seeing both arms across sessions.
- **Decision:** ship if primary metric lift's CI excludes 0 and no guardrail regresses beyond pre-set thresholds; otherwise iterate.

## Experiment 2 — generic card text vs "why it fits" text
- **Hypothesis:** grounded reasons raise save rate and lower "irrelevant" feedback.
- **Control:** catalogue description snippet. **Treatment:** reasoned explanation (template or grounded-LLM).
- **Eligible / unit / logging:** as Experiment 1; run on the treatment retrieval arm only to isolate the text effect (factorial design is possible with more traffic).
- **Primary metric:** save rate per viewed item (cluster-robust by session). **Guardrails:** latency, LLM cost per completed task (if LLM used), verification failure rate, complaint rate.
- **Sample size:** same formula; item-level clustering inflates it, so use session-level analysis or a design-effect correction.
- **Confounders:** text length, card position, explanation accuracy differences, interaction with Experiment 1.
- **Decision:** ship if save rate rises with CI excluding 0 and cost per completed task stays inside budget.

## Before any real test
Run an A/A test to validate assignment and metrics, pre-register hypotheses and thresholds, and confirm event quality.

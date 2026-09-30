# Limitations

**Data:** entirely synthetic (invented prices/stock/attributes); templated descriptions; no images; no real popularity signals.
**Users:** no real users, interviews, or usage data. Every user-benefit statement is a hypothesis.
**Evaluation:** relevance labels are derived from the same catalogue tags the ranker uses, so precision numbers are optimistic (partly circular). Only 30 queries, written by the author. Latency is from a single-core sandbox with a 283-item catalogue.
**Retrieval/ranking:** BM25 with a hand-built interest lexicon (20 interests); no semantic matching; ranking weights untuned; "generic gift" is a synthetic attribute.
**Intent parsing:** rule-based; English only; misparses are possible (e.g., unusual budget phrasing, sarcasm); ambiguous words can be treated as keywords.
**LLM:** optional path implemented and unit-tested with fakes only; not exercised against a live provider; model name is configurable and unverified here.
**Product:** single profile, no auth, no purchase flow, no partner integrations; impression logging is at result return, not viewport.
**UI:** verified headlessly (Streamlit `AppTest` + server health check), not visually inspected in a browser; no screenshots captured; mobile layout untested.
**Experiments:** assignment and logging exist, but no live test was run; no significance claims are made.
**Security:** regex injection screen; no auth, encryption at rest, or rate limits.

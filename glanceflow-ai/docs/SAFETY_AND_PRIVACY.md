# Safety and privacy

## Controls implemented (each has a test)
| Risk | Control | Test |
|---|---|---|
| Budget/stock/exclusion violations | hard filter before ranking + critic re-check against the catalogue | test_verification, test_orchestration |
| Hallucinated item IDs / tampered facts | critic looks every item up in the catalogue and compares price/title/availability | test_hallucinated_id_rejected, test_tampered_price_detected |
| LLM invents price/attributes | explanations accepted only if any ₹ amount equals the item price or user budget; else template | test_ungrounded_explanation_rejected, test_llm_hallucinated_price_falls_back |
| LLM invents constraints | extracted budget must appear in the request text; interests must be substrings | test_llm_cannot_invent_budget |
| Prompt injection in catalogue text | screened at ingestion (quarantine), at discovery, and by the critic; catalogue text is never sent as instructions; UI HTML-escapes it | test_injection_* |
| Unsupported purchase | intent flags it; action agent rejects `purchase` | test_purchase_action_is_unsupported |
| Fake success | actions re-read storage before reporting success; failures return explicit statuses | test_failed_persistence_never_reports_success |
| Runaway loops | ≤1 revision, transition table, 12-step cap, bounded retries | test_revision_is_bounded, test_state_machine_* |
| Repeated actions | idempotent save/dismiss | test_repeated_save_is_idempotent |
| Unauthorised actions | must have been shown this session (or be in the shortlist) | test_cannot_act_on_unseen_item |

## Privacy
Local SQLite; no network calls unless the user configures a provider **and** toggles it on. Events store structured properties and `query_chars`, not prompt text. Stored preferences contain only what the user typed in requests and are shown in Settings. Clear history / reset profile deletes all tables' user data.

## Caveats
- The injection screen is a regex list: it will miss novel phrasings. Defence in depth reduces but does not eliminate risk.
- The live LLM path was never run against a real API here.
- Single demo profile, no authentication, no encryption at rest, no rate limiting: not production-ready.

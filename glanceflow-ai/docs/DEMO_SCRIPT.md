# Demo script (~4 minutes)

**Setup:** `python3 scripts/generate_data.py && python3 scripts/initialize_db.py && streamlit run app.py`. In Analytics, click *Load seeded demo data* only if you want the dashboard populated; say clearly that it is seeded.

1. **Frame (20s):** "Independent prototype, synthetic catalogue, not Glance data. The hypothesis: intent-aware, explained, verified discovery reduces effort."
2. **Discover (30s):** paste the example prompt. Note the empty/starter feed is labelled "not personalised yet".
3. **Results (60s):** point at constraint chips (budget ₹1,500, interest reading, prefers practical, avoid generic), the "within budget" and "verified vs catalogue" badges, and the reasons. Save two items.
4. **Refine (30s):** click *Cheaper* (budget becomes ₹1,125); then type "actually she's into cooking now" to show interests being replaced.
5. **Compare + Shortlist (30s):** compare two items; open Shortlist; remove one to show the confirmation step.
6. **Guardrails (30s):** "Buy this for me now" → refusal. "Gift under ₹500 but at least ₹900" → one clarification. "Scuba diving under ₹100" → honest empty state.
7. **Agent activity (30s):** show stages, tools, timings, verification result. Say: "summaries only, no chain-of-thought".
8. **Analytics + Settings (30s):** live vs seeded toggle; metric definitions; clear/reset; external API is off by default.
9. **Close (15s):** "Offline benchmark: violations 44%→0% and precision@5 0.44→0.97 on synthetic data. That's not real-world proof; next step is an A/A then A/B test."

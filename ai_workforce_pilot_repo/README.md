# AI Workforce Exposure & Reskilling Investment Strategy (pilot)
Question: how exposed is IT-BPM work to generative AI, and how should a fixed workforce budget be split across reskill, redeploy, hire and redesign?
Scope: 3 occupations (Software Developers, QA Analysts and Testers, Customer Service Representatives), 60 O*NET tasks, hypothetical 10,000-person client, INR, 3 years.
Run: `pip install -r requirements.txt && python run_pilot.py && python src/figures.py && pytest`
Layout: src/scoring.py (rubric, validation, scores), src/model.py (aggregation, economics, MILP, robustness), src/figures.py, tests/, data/, outputs/, docs/.
Read first: CASE_STUDY.md, docs/validation_checklist.md (what is and is not done), docs/assumptions.md.
Deck: https://claude.ai/artifact/6vcnmEQNNLP29WLcvAjGqH
Licences: O*NET data CC BY 4.0; ILO WP140 CC BY 4.0. India-vs-US selection: only India data (ILO, Labour Bureau) was assembled; the US option was not evaluated.

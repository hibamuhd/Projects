# Data dictionary
- data/raw/onet_*: O*NET OnLine task statements (task_id, importance, core/supplemental, statement, source_url, retrieved). CSR file is the unmodified user download.
- data/processed/ilo_wp140_tableA1_isco08.csv: ILO WP140 Table A1 (gradient, isco08_code, occupation_name, mean_score, sd_score).
- data/processed/ils_qes_itbpo_employment.csv: Indian Labour Statistics 2022&2023 Table 2.14 IT/BPO estimates (context only; not used in the model).
- data/processed/scored_tasks.csv: tasks + five 0-4 scores, confidence, rationale, scorer, date, rubric version.
- outputs/: occupation_exposure, allocation_by_strategy, strategy_comparison, sensitivity, threshold_robustness, results.json, human_validation_template.csv, figures/.
- docs/source_register.csv: provenance for every input.

# Scoring rubric and model card (rubric v1.0)
Scorer: Claude Sonnet 5.5, in-conversation, single pass, 2026-10-15. 60 O*NET tasks (Software Developers 17, QA Analysts and Testers 30, Customer Service Representatives 13).
Scales 0-4: exposure (information processing GenAI could affect), automation (executable with limited human intervention), augmentation (productivity gain with employee accountable), human judgment (judgment, interpersonal work, verification that stays human), feasibility (integration, data, security, regulation).
Each row also stores confidence (L/M/H) and a short rationale. No claim is made about actual deployment, realised productivity or job loss.
Known limits: one model, one pass, no repeated-run stability test, no human labels yet (use outputs/human_validation_template.csv, then scoring.qwk). The same model family helped design the project, so self-assessment bias is possible.
Aggregation: importance-weighted task means (tasks without importance rating get zero weight; equal weighting tested). ILO Table 5 gradient rules applied; mu>=0.6 with high spread is treated as Gradient 3 (our extension).
O*NET-SOC to ISCO-08 mapping is analyst-assigned (15-1252 to 2512, 15-1253 to 2519, 43-4051 to 4222), not the official crosswalk.

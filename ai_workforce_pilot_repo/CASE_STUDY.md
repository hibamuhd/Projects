# Case study: where should an IT-BPM firm spend its AI workforce budget?
**Decision.** A CHRO of a hypothetical 10,000-person IT-BPM firm has a fixed budget (INR 25 crore, assumed) and four moves: reskill, redeploy, hire, or redesign work and monitor. Pilot scope: developers (3,000), QA testers (1,200), customer service (3,000).

**Approach.** I scored 60 O*NET tasks on five 0-4 dimensions (exposure, automation, augmentation, human judgment, feasibility) with a versioned rubric, aggregated them by task importance, and benchmarked against the ILO's 2025 index (WP140 Table A1). Exposure, automability, adoption and displacement are kept separate. A 3-year INR model values each move per employee, and an integer program picks headcounts under budget, training-capacity, redeployment-demand and coverage constraints. It is compared with equal-budget, most-exposed-first and no-action strategies and stress-tested on 11 drivers.

**Findings.** (1) Customer service is most exposed (0.85) and developers least (0.63), matching the ILO ranking; automation scores sit 0.01-0.14 from the ILO means. (2) Developers keep the most human-led work (51% of task weight vs 5% in customer service). (3) Per employee, redesign-and-monitor beats reskilling for developers (+INR 39k vs +19k) and QA; reskilling destroys value in customer service (-INR 43k). (4) The optimised portfolio, 2,820 developers and 1,128 QA on redesign plus 432 redeployments, returns NPV INR 17.9 crore (ROI 98%, payback year 2) against -8.7 crore for reskilling the most exposed role first.

**Recommendation.** Redesign work and monitor for developers and QA, redeploy up to 6% of each role into higher-demand roles, hold reskilling until measured costs are known, and make no headcount cuts on exposure alone. Review at a month-12 gate.

**Economics and robustness.** NPV stays positive in every single-factor test (INR 6.0-30.8 crore); it depends most on AI adoption and productivity realisation, and benefits can fall about 50% before NPV reaches zero. Reskilling enters only if training cost falls 30% or its productivity multiplier reaches 1.7.

**Limits.** Three occupations; single-pass LLM scoring without human validation or stability tests; wages, costs, adoption and headcount are assumptions; occupation mapping is analyst-assigned; results are modelled, not realised. Client wage, headcount and attrition data would improve it most.


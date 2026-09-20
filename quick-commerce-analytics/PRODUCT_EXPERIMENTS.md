# Product Analytics Angle: Experiments Suggested by This Analysis

These are **hypothetical experiment designs** motivated by the descriptive analysis in this project — no experiment was actually run, and no results exist. Use these to demonstrate product-analytics thinking in an interview, framed explicitly as "here's what I'd test next," never as completed work.

## Experiment 1 — Second-Order Activation Nudge

- **Hypothesis:** A personalized reminder/incentive sent after a customer's first order increases the rate of a second order within 14 days.
- **Target users:** All first-time customers (order_number = 1 completed, no second order yet)
- **Control:** No intervention (current experience)
- **Treatment:** Push/email reminder with a personalized reorder suggestion, sent 5-7 days after first order
- **Primary metric:** Order-1 → Order-2 conversion rate within 14 days
- **Secondary metrics:** Time-to-second-order, basket size of second order
- **Guardrail metrics:** Unsubscribe/opt-out rate, support ticket volume (fatigue signal)
- **Expected mechanism:** Reduces the drop-off identified in `INSIGHTS.md` (Order-1 → Order-2), by prompting habit formation before intent decays

## Experiment 2 — Reorder-Led Homepage Ranking

- **Hypothesis:** Surfacing a customer's frequently-reordered products earlier in the shopping journey (e.g. a "Reorder your usuals" module above the fold) increases average basket size.
- **Target users:** Repeat customers (segment: repeat or high_frequency, per `dim_customer.customer_segment`)
- **Control:** Standard homepage/category-first layout
- **Treatment:** Personalized reorder module shown first
- **Primary metric:** Average basket size (items per order)
- **Secondary metrics:** Time-to-first-add-to-cart, category diversity per order
- **Guardrail metrics:** Overall conversion rate (make sure the module doesn't cannibalize discovery of new products)
- **Expected mechanism:** Reduces search friction for known-purchase products, freeing cognitive room for additional add-ons

## Experiment 3 — Delivery-Speed Impact on Repeat Behavior

- **Hypothesis:** Faster delivery increases the probability of a repeat purchase within 30 days.
- **Target users:** New customers, randomized at fulfillment (requires operational A/B capability, e.g. routing a subset through an expedited fulfillment path)
- **Control:** Standard delivery SLA
- **Treatment:** Expedited delivery SLA
- **Primary metric:** Repeat-purchase rate within 30 days
- **Secondary metrics:** Customer satisfaction/NPS, delivery cost per order
- **Guardrail metrics:** Delivery cost increase, driver/rider utilization
- **Expected mechanism:** Motivated by the exploratory (synthetic-data) correlation in `sql/06_delivery_analysis.sql` — treated here strictly as a hypothesis to validate with real operational data, not a proven causal claim, since the underlying delivery data in this project is simulated (see `LIMITATIONS.md`)

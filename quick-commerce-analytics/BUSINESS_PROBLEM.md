# Business Problem

## Core Question

> How can a quick-commerce/food-delivery platform improve customer retention and order frequency by understanding reorder behavior, delivery performance, customer cohorts, and purchasing patterns?

This project treats the Instacart dataset as a stand-in for a quick-commerce platform (e.g. Blinkit, Zepto) and answers the question across three lenses:

## 1. Customer / Retention
- What % of orders are reorders?
- Which cohorts show the highest repeat-purchase behavior?
- How does retention change after the first order (order-2, order-3, ... order-N)?
- What % of customers place only one order ("one-and-done")?
- How does reorder behavior vary by product/department?

## 2. Delivery / Operations (synthetic layer — see LIMITATIONS.md)
- Delivery-time distribution, mean/median/P90/P95
- Late-delivery rate
- Delivery time by hour-of-day / day-of-week
- Whether delivery performance is associated with repeat behavior

## 3. Product / Order Behavior
- Top products/departments by volume and by reorder rate
- Average basket size and its distribution
- Orders per customer
- Order timing patterns (hour/day) as a proxy for demand shape

## Why This Matters for a Quick-Commerce Business

Reorder rate and early-lifecycle retention are the two levers that most directly drive repeat GMV in a subscription-adjacent, high-frequency category like groceries — the same dynamic Blinkit/Zepto/Instacart all compete on. A platform that can identify *where* in the customer lifecycle it loses people, and *which* products/categories carry the highest reorder gravity, has a concrete lever for retention interventions (reminders, bundling, replenishment prompts) rather than generic marketing spend.

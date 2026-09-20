# Quick-Commerce & Food Delivery Analytics
### Reorder, Delivery & Cohort Intelligence Dashboard

A business/product analytics project analyzing customer reorder behavior, retention cohorts, and (synthetic) delivery performance for a quick-commerce/food-delivery context — built on the public Instacart Market Basket Analysis dataset.

## Business Problem

> How can a quick-commerce/food-delivery platform improve customer retention and order frequency by understanding reorder behavior, delivery performance, customer cohorts, and purchasing patterns?

See [`BUSINESS_PROBLEM.md`](BUSINESS_PROBLEM.md) for the full framing.

## Dataset

**Primary:** [Instacart Market Basket Analysis](https://www.kaggle.com/c/instacart-market-basket-analysis) (public, Kaggle) — 3M+ grocery orders, 200K+ users.

**Secondary (synthetic):** A clearly labeled synthetic delivery-operations extension, since Instacart contains no delivery-time or price fields. See [`DATA_SOURCE.md`](DATA_SOURCE.md) and [`LIMITATIONS.md`](LIMITATIONS.md).

## Tech Stack

- **Python** (pandas, numpy, matplotlib/seaborn) — cleaning, feature engineering, cohort/reorder logic
- **SQL** — business metric queries (SQLite-compatible; portable to MySQL/Postgres)
- **Power BI + DAX** — final interactive dashboard
- **Git/GitHub-ready** structure

## Architecture

```
Raw Data (Instacart CSVs)
   ↓
Python Cleaning (02_data_cleaning.py)
   ↓
Feature Engineering (03_feature_engineering.py) + Synthetic Delivery Layer
   ↓
SQL Transformations (sql/*.sql) → analytical tables
   ↓
Star-Schema Data Model (powerbi/data_model.md)
   ↓
DAX Measures (powerbi/dax_measures.md)
   ↓
Power BI Dashboard (4 pages)
   ↓
Business Insights (INSIGHTS.md)
```

## Key Metrics Tracked

Reorder rate (overall/product/department/cohort), repeat-customer rate, order-number retention curve, basket size, delivery-time percentiles (synthetic), reorder rate vs. tenure.

## Dashboard Pages

1. Executive Overview
2. Customer Retention & Cohorts
3. Reorder & Product Analytics
4. Delivery & Operations (synthetic layer)

## Key Insights & Business Recommendations

Populated in [`INSIGHTS.md`](INSIGHTS.md) **after** you run the pipeline on the real dataset — this repo ships with the methodology and structure, not pre-filled numbers (see `LIMITATIONS.md` for why).

## How to Run

See [`START_HERE.md`](START_HERE.md) for the full walkthrough, or [`SETUP.md`](SETUP.md) for a terse checklist.

## Power BI Setup

See [`powerbi/README.md`](powerbi/README.md).

## Project Structure

```
quick-commerce-analytics/
├── README.md, BUSINESS_PROBLEM.md, DATA_SOURCE.md, DATA_DICTIONARY.md,
│   INSIGHTS.md, LIMITATIONS.md, SETUP.md, START_HERE.md
├── data/{raw,processed,synthetic}/
├── python/   — 01_data_loading, 02_data_cleaning, 03_feature_engineering,
│               04_cohort_analysis, 05_eda, 06_generate_synthetic_delivery
├── sql/      — 01_data_validation ... 06_delivery_analysis
├── powerbi/  — data_model, dax_measures
├── notebooks/exploratory_analysis.ipynb
├── visuals/dashboard_mockup.png
└── requirements.txt
```

## Future Improvements

- Swap the synthetic delivery layer for a real delivery-time dataset (e.g. a Kaggle food-delivery-time dataset) joined on order timing features.
- Add a lightweight logistic regression for reorder propensity (optional, non-essential to the core BI story).
- Automate the Python → SQL → Power BI refresh with a scheduled pipeline.

## Author

Hiba Muhammed — built as a portfolio project 

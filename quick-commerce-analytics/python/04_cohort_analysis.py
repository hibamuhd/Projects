"""
04_cohort_analysis.py

Builds a TENURE-BASED cohort retention table (see LIMITATIONS.md for why
this replaces a calendar-month cohort matrix: Instacart has no real order
dates, only order_number and days_since_prior_order).

Cohort definition:
  - Every user's cohort anchor is their order_number == 1 (their first order).
  - "Retention at order N" = % of the full user base that placed at least N
    orders (i.e. reached order_number == N).

Output: cohort_retention.csv with columns [order_number, users_reaching,
cohort_size, retention_pct] — plug this straight into a Power BI line chart
or retention curve visual.

"""

import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

MAX_ORDER_NUMBER_TO_TRACK = 20  # cap the curve at a reasonable tenure depth


def main():
    dim_customer = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_customer.csv"))

    cohort_size = dim_customer["user_id"].nunique()
    rows = []
    for n in range(1, MAX_ORDER_NUMBER_TO_TRACK + 1):
        users_reaching = (dim_customer["total_orders"] >= n).sum()
        retention_pct = round(100 * users_reaching / cohort_size, 2)
        rows.append({
            "order_number": n,
            "users_reaching": int(users_reaching),
            "cohort_size": int(cohort_size),
            "retention_pct": retention_pct,
        })

    cohort_retention = pd.DataFrame(rows)
    cohort_retention.to_csv(os.path.join(PROCESSED_DIR, "cohort_retention.csv"), index=False)

    print("Tenure-based cohort retention curve:")
    print(cohort_retention.to_string(index=False))
    print("\nWritten to data/processed/cohort_retention.csv")
    print(f"\nOrder-1 -> Order-2 drop-off: "
          f"{cohort_retention.loc[0, 'retention_pct'] - cohort_retention.loc[1, 'retention_pct']:.2f} pts")


if __name__ == "__main__":
    main()

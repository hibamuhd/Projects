"""
05_eda.py

Exploratory analysis: reorder rates, basket size distribution, order timing
patterns, and their relationships. Saves charts to visuals/ for the README
and for sanity-checking before building the Power BI dashboard.

Run after 03_feature_engineering.py (04_cohort_analysis.py optional first).
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
VISUALS_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals")
os.makedirs(VISUALS_DIR, exist_ok=True)


def main():
    fact_orders = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_orders.csv"))

    overall_reorder_rate = fact_orders["reordered"].mean()
    print(f"Overall reorder rate: {overall_reorder_rate:.2%}")

    # Reorder rate by department
    dept_reorder = (
        fact_orders.groupby("department")["reordered"]
        .mean()
        .sort_values(ascending=False)
    )
    print("\nTop 5 departments by reorder rate:")
    print(dept_reorder.head())

    fig, ax = plt.subplots(figsize=(10, 6))
    dept_reorder.plot(kind="barh", ax=ax)
    ax.set_xlabel("Reorder rate")
    ax.set_title("Reorder rate by department")
    plt.tight_layout()
    fig.savefig(os.path.join(VISUALS_DIR, "reorder_rate_by_department.png"), dpi=150)
    plt.close(fig)

    # Basket size distribution
    basket_size = fact_orders.groupby("order_id")["product_id"].count()
    fig, ax = plt.subplots(figsize=(8, 5))
    basket_size.plot(kind="hist", bins=40, ax=ax)
    ax.set_xlabel("Items per order")
    ax.set_title("Basket size distribution")
    plt.tight_layout()
    fig.savefig(os.path.join(VISUALS_DIR, "basket_size_distribution.png"), dpi=150)
    plt.close(fig)

    # Reorder rate by order_number (tenure effect)
    reorder_by_tenure = fact_orders.groupby("order_number")["reordered"].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    reorder_by_tenure.plot(ax=ax, marker="o")
    ax.set_xlabel("Order number (tenure)")
    ax.set_ylabel("Reorder rate")
    ax.set_title("Reorder rate vs. customer tenure")
    plt.tight_layout()
    fig.savefig(os.path.join(VISUALS_DIR, "reorder_rate_vs_tenure.png"), dpi=150)
    plt.close(fig)

    # Order timing heatmap-style summary (hour x day-of-week order volume)
    timing = fact_orders.drop_duplicates("order_id").pivot_table(
        index="order_dow", columns="order_hour_of_day", values="order_id", aggfunc="count"
    )
    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(timing, aspect="auto", cmap="viridis")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Day of week (0=Sun per Instacart convention)")
    ax.set_title("Order volume by day-of-week x hour-of-day")
    fig.colorbar(im, ax=ax, label="Order count")
    plt.tight_layout()
    fig.savefig(os.path.join(VISUALS_DIR, "order_timing_heatmap.png"), dpi=150)
    plt.close(fig)

    print(f"\nCharts saved to {VISUALS_DIR}/")


if __name__ == "__main__":
    main()

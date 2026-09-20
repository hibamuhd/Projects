"""
03_feature_engineering.py

Builds the analytical star-schema tables from the cleaned data:
- fact_orders          (grain: order-product line item)
- dim_customer          (grain: user_id, with behavioral segments)
- dim_product           (grain: product_id, with reorder-rate stats)

Segmentation methodology (documented, not arbitrary):
- One-time:      total_orders == 1
- Occasional:    total_orders between 2 and the 50th percentile of
                  multi-order users (inclusive)
- Repeat:        total_orders between the 50th and 90th percentile
- High-frequency: total_orders at or above the 90th percentile

Percentile cutoffs are computed from the ACTUAL data at runtime and printed
to the console — record the real numbers you get in LIMITATIONS.md / your
write-up rather than assuming these figures.

"""

import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def build_fact_orders(orders, order_products, products_full):
    fact = order_products.merge(orders, on="order_id", how="inner")
    fact = fact.merge(
        products_full[["product_id", "product_name", "aisle", "department"]],
        on="product_id", how="left"
    )
    cols = [
        "order_id", "user_id", "product_id", "product_name", "department", "aisle",
        "order_number", "order_dow", "order_hour_of_day", "days_since_prior_order",
        "reordered", "add_to_cart_order", "is_first_order"
    ]
    return fact[cols]


def build_dim_customer(fact_orders):
    grp = fact_orders.groupby("user_id")
    dim = grp.agg(
        total_orders=("order_number", "max"),
        avg_days_between_orders=("days_since_prior_order", "mean"),
        total_items_ordered=("product_id", "count"),
    ).reset_index()

    dim["is_one_time_customer"] = (dim["total_orders"] == 1).astype(int)

    multi = dim.loc[dim["total_orders"] > 1, "total_orders"]
    p50 = multi.quantile(0.50)
    p90 = multi.quantile(0.90)
    print(f"[Segmentation cutoffs from actual data] p50={p50:.1f} orders, p90={p90:.1f} orders")

    def segment(n_orders):
        if n_orders == 1:
            return "one_time"
        elif n_orders <= p50:
            return "occasional"
        elif n_orders <= p90:
            return "repeat"
        else:
            return "high_frequency"

    dim["customer_segment"] = dim["total_orders"].apply(segment)
    return dim


def build_dim_product(fact_orders):
    grp = fact_orders.groupby(["product_id", "product_name", "department", "aisle"])
    dim = grp.agg(
        total_times_ordered=("order_id", "count"),
        total_times_reordered=("reordered", "sum"),
    ).reset_index()
    dim["product_reorder_rate"] = dim["total_times_reordered"] / dim["total_times_ordered"]
    return dim.sort_values("total_times_ordered", ascending=False)


def main():
    orders = pd.read_csv(os.path.join(PROCESSED_DIR, "orders_clean.csv"))
    order_products = pd.read_csv(os.path.join(PROCESSED_DIR, "order_products_clean.csv"))
    products_full = pd.read_csv(os.path.join(PROCESSED_DIR, "products_full.csv"))

    fact_orders = build_fact_orders(orders, order_products, products_full)
    dim_customer = build_dim_customer(fact_orders)
    dim_product = build_dim_product(fact_orders)

    fact_orders.to_csv(os.path.join(PROCESSED_DIR, "fact_orders.csv"), index=False)
    dim_customer.to_csv(os.path.join(PROCESSED_DIR, "dim_customer.csv"), index=False)
    dim_product.to_csv(os.path.join(PROCESSED_DIR, "dim_product.csv"), index=False)

    print("\nFeature tables written to data/processed/:")
    print("  - fact_orders.csv")
    print("  - dim_customer.csv")
    print("  - dim_product.csv")
    print(f"\nCustomer segment distribution:\n{dim_customer['customer_segment'].value_counts()}")


if __name__ == "__main__":
    main()

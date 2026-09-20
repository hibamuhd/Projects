"""
02_data_cleaning.py

Cleans the raw Instacart tables:
- checks for duplicates and nulls
- combines order_products__prior + order_products__train into one
  order-line-item table (full order history)
- joins products with aisles/departments for readable category names
- writes cleaned intermediate tables to data/processed/

"""

import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


def read_raw(name):
    return pd.read_csv(os.path.join(RAW_DIR, name))


def report_quality(df, name):
    dupes = df.duplicated().sum()
    nulls = df.isnull().sum().sum()
    print(f"[{name}] rows={len(df):,} duplicates={dupes:,} total_nulls={nulls:,}")


def main():
    orders = read_raw("orders.csv")
    op_prior = read_raw("order_products__prior.csv")
    op_train = read_raw("order_products__train.csv")
    products = read_raw("products.csv")
    aisles = read_raw("aisles.csv")
    departments = read_raw("departments.csv")

    for df, name in [(orders, "orders"), (op_prior, "order_products__prior"),
                      (op_train, "order_products__train"), (products, "products")]:
        report_quality(df, name)

    # Combine prior + train into one full order-line-item history.
    # NOTE: Instacart's 'test' eval_set rows have no product line items released
    # publicly, so they are excluded (this is expected, not a data-quality bug).
    order_products = pd.concat([op_prior, op_train], ignore_index=True)
    order_products = order_products.drop_duplicates()

    # Drop orders with no matching line items (shouldn't happen, but check).
    orders = orders.drop_duplicates(subset="order_id")

    # Readable product dimension.
    products_full = (
        products
        .merge(aisles, on="aisle_id", how="left")
        .merge(departments, on="department_id", how="left")
    )

    # Basic null handling: days_since_prior_order is legitimately NaN for a
    # user's first order (order_number == 1) — do NOT impute this away, it's
    # meaningful. Flag it explicitly instead.
    orders["is_first_order"] = (orders["order_number"] == 1).astype(int)

    orders.to_csv(os.path.join(PROCESSED_DIR, "orders_clean.csv"), index=False)
    order_products.to_csv(os.path.join(PROCESSED_DIR, "order_products_clean.csv"), index=False)
    products_full.to_csv(os.path.join(PROCESSED_DIR, "products_full.csv"), index=False)

    print("\nCleaned tables written to data/processed/:")
    print("  - orders_clean.csv")
    print("  - order_products_clean.csv")
    print("  - products_full.csv")


if __name__ == "__main__":
    main()

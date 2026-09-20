"""
01_data_loading.py

Loads the six raw Instacart CSVs from data/raw/, validates that expected
files and columns exist, and prints basic shape/health diagnostics.

"""

import os
import sys
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")

EXPECTED_FILES = {
    "orders.csv": ["order_id", "user_id", "eval_set", "order_number",
                    "order_dow", "order_hour_of_day", "days_since_prior_order"],
    "order_products__prior.csv": ["order_id", "product_id", "add_to_cart_order", "reordered"],
    "order_products__train.csv": ["order_id", "product_id", "add_to_cart_order", "reordered"],
    "products.csv": ["product_id", "product_name", "aisle_id", "department_id"],
    "aisles.csv": ["aisle_id", "aisle"],
    "departments.csv": ["department_id", "department"],
}


def load_and_validate():
    dataframes = {}
    missing_files = []

    for filename, expected_cols in EXPECTED_FILES.items():
        path = os.path.join(RAW_DIR, filename)
        if not os.path.exists(path):
            missing_files.append(filename)
            continue

        df = pd.read_csv(path)
        missing_cols = set(expected_cols) - set(df.columns)
        if missing_cols:
            print(f"[WARN] {filename} is missing expected columns: {missing_cols}")

        dataframes[filename.replace(".csv", "")] = df
        print(f"[OK] Loaded {filename}: {df.shape[0]:,} rows x {df.shape[1]} cols")

    if missing_files:
        print("\n[ERROR] Missing required files in data/raw/:")
        for f in missing_files:
            print(f"  - {f}")
        print("\nSee DATA_SOURCE.md for download instructions.")
        sys.exit(1)

    return dataframes


if __name__ == "__main__":
    dfs = load_and_validate()
    print("\nAll raw files loaded successfully.")
    print(f"Total users: {dfs['orders']['user_id'].nunique():,}")
    print(f"Total orders: {dfs['orders']['order_id'].nunique():,}")
    print(f"Total products: {dfs['products']['product_id'].nunique():,}")

"""
06_generate_synthetic_delivery.py

Generates a CLEARLY SYNTHETIC delivery-time extension, since Instacart has
no real delivery timestamps. This is NOT derived from real operational data
of any company — it is a parameterized simulation used only to demonstrate
delivery-analytics dashboard design (percentiles, late-rate, hour-of-day
patterns).


Method (documented so it's fully reproducible and auditable):
  base_time = 25 minutes
  + peak-hour penalty: +8 min if order_hour_of_day in [12,13,18,19,20]
  + basket-size penalty: +0.4 min per item in the order (pick-time proxy)
  + random noise: Normal(0, 6) minutes, floored at 8 minutes minimum


"""

import os
import numpy as np
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
SYNTHETIC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
os.makedirs(SYNTHETIC_DIR, exist_ok=True)

RANDOM_SEED = 42
PEAK_HOURS = {12, 13, 18, 19, 20}
BASE_MINUTES = 25
PEAK_PENALTY_MINUTES = 8
PER_ITEM_MINUTES = 0.4
NOISE_STD = 6
MIN_MINUTES = 8
LATE_THRESHOLD_MINUTES = 45


def main():
    rng = np.random.default_rng(RANDOM_SEED)

    orders = pd.read_csv(os.path.join(PROCESSED_DIR, "orders_clean.csv"))
    fact_orders = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_orders.csv"))

    basket_size = fact_orders.groupby("order_id")["product_id"].count().rename("basket_size")
    orders = orders.merge(basket_size, on="order_id", how="left")
    orders["basket_size"] = orders["basket_size"].fillna(1)

    is_peak = orders["order_hour_of_day"].isin(PEAK_HOURS).astype(int)
    noise = rng.normal(0, NOISE_STD, size=len(orders))

    delivery_time = (
        BASE_MINUTES
        + is_peak * PEAK_PENALTY_MINUTES
        + orders["basket_size"] * PER_ITEM_MINUTES
        + noise
    )
    delivery_time = np.maximum(delivery_time, MIN_MINUTES)

    synthetic_delivery = pd.DataFrame({
        "order_id": orders["order_id"],
        "delivery_time_minutes": delivery_time.round(1),
        "is_late": (delivery_time > LATE_THRESHOLD_MINUTES).astype(int),
        "is_synthetic": 1,
    })

    out_path = os.path.join(SYNTHETIC_DIR, "synthetic_delivery.csv")
    synthetic_delivery.to_csv(out_path, index=False)

    print(f"Synthetic delivery data written to {out_path}")
    print(synthetic_delivery["delivery_time_minutes"].describe())
    print(f"Late-delivery rate (synthetic): {synthetic_delivery['is_late'].mean():.2%}")


if __name__ == "__main__":
    main()

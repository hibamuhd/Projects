# Data Dictionary

## Raw tables (from Instacart)

### `orders`
| Column | Type | Description |
|---|---|---|
| order_id | int | Unique order identifier |
| user_id | int | Unique customer identifier |
| eval_set | string | `prior`/`train`/`test` (Instacart's original ML split — we use prior+train as full order history) |
| order_number | int | Sequence number of this order for the user (1 = first order) |
| order_dow | int | Day of week (0-6) |
| order_hour_of_day | int | Hour of day (0-23) |
| days_since_prior_order | float | Days since the user's previous order (NaN for order_number = 1) |

### `order_products__prior` / `order_products__train`
| Column | Type | Description |
|---|---|---|
| order_id | int | FK to orders |
| product_id | int | FK to products |
| add_to_cart_order | int | Position item was added to cart |
| reordered | int (0/1) | 1 if the customer ordered this product in a previous order |

### `products` / `aisles` / `departments`
Standard lookup tables: `product_id → product_name, aisle_id, department_id`; `aisle_id → aisle`; `department_id → department`.

## Processed / derived tables (built by `python/03_feature_engineering.py`)

### `fact_orders` (grain: one row per order-product line item)
order_id, user_id, product_id, department, aisle, order_number, order_dow, order_hour_of_day, days_since_prior_order, reordered, add_to_cart_order

### `dim_customer`
user_id, total_orders, first_order_number (=1, by definition), max_order_number, avg_days_between_orders, customer_segment (see LIMITATIONS.md for segmentation logic), is_one_time_customer

### `dim_product`
product_id, product_name, aisle, department, total_times_ordered, total_times_reordered, product_reorder_rate

### `cohort_retention` (grain: cohort × order_number)
cohort_size, order_number, users_reaching_this_order, retention_pct

> **Note on cohorts:** Instacart has no calendar order date — only `order_number` and relative `days_since_prior_order`. So "cohort" here is defined as **tenure-based** (all users grouped at their order_number = 1, i.e. their first order), and retention is tracked by *order sequence* (order 1 → order 2 → order 3...), not by calendar month. This is explained in full in `LIMITATIONS.md` — it is the honest substitute for the calendar-month cohort matrix, since the public dataset does not contain real dates.

### `synthetic_delivery` (data/synthetic/, joined on order_id)
order_id, delivery_time_minutes (synthetic), is_late (synthetic, threshold defined in script), is_synthetic = 1

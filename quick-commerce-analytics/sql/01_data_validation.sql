-- 01_data_validation.sql
-- Sanity checks to run against the processed tables (loaded into SQLite/
-- MySQL/Postgres from data/processed/*.csv). Assumes tables:
-- fact_orders, dim_customer, dim_product, cohort_retention.

-- 1. Row counts (should match Python script output)
SELECT 'fact_orders' AS table_name, COUNT(*) AS row_count FROM fact_orders
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product;

-- 2. Null checks on key columns
SELECT
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS null_order_id,
    SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END) AS null_user_id,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) AS null_product_id
FROM fact_orders;

-- 3. days_since_prior_order should ONLY be null for order_number = 1
SELECT order_number, COUNT(*) AS row_count
FROM fact_orders
WHERE days_since_prior_order IS NULL
GROUP BY order_number;

-- 4. reordered flag should only ever be 0 or 1
SELECT DISTINCT reordered FROM fact_orders;

-- 5. Duplicate order-product line items (should be zero)
SELECT order_id, product_id, COUNT(*) AS dupe_count
FROM fact_orders
GROUP BY order_id, product_id
HAVING COUNT(*) > 1;

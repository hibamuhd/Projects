-- 03_reorder_metrics.sql
-- Reorder rate at overall, department, product, and tenure (order_number) level.
-- Overall reorder rate

SELECT ROUND(100.0 * AVG(reordered), 2) AS overall_reorder_rate_pct
FROM fact_orders;

-- Reorder rate by department
SELECT
    department,
    COUNT(*) AS total_line_items,
    SUM(reordered) AS reordered_line_items,
    ROUND(100.0 * SUM(reordered) / COUNT(*), 2) AS reorder_rate_pct
FROM fact_orders
GROUP BY department
ORDER BY reorder_rate_pct DESC;

-- Top 20 reordered products (by volume, min 100 orders to avoid noise)
SELECT
    product_id,
    product_name,
    total_times_ordered,
    total_times_reordered,
    ROUND(100.0 * product_reorder_rate, 2) AS reorder_rate_pct
FROM dim_product
WHERE total_times_ordered >= 100
ORDER BY product_reorder_rate DESC
LIMIT 20;

-- Bottom 20 reordered products (min 100 orders)
SELECT
    product_id,
    product_name,
    total_times_ordered,
    total_times_reordered,
    ROUND(100.0 * product_reorder_rate, 2) AS reorder_rate_pct
FROM dim_product
WHERE total_times_ordered >= 100
ORDER BY product_reorder_rate ASC
LIMIT 20;

-- Reorder rate by order_number (tenure effect — do reorders become more likely
-- as a customer becomes more established?)
SELECT
    order_number,
    COUNT(*) AS total_line_items,
    ROUND(100.0 * AVG(reordered), 2) AS reorder_rate_pct
FROM fact_orders
WHERE order_number <= 20
GROUP BY order_number
ORDER BY order_number;

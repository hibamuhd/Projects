-- 05_product_analysis.sql
-- Product/department/basket-level analytics.

-- Top departments by order volume
SELECT
    department,
    COUNT(*) AS total_line_items,
    COUNT(DISTINCT order_id) AS orders_containing_dept
FROM fact_orders
GROUP BY department
ORDER BY total_line_items DESC;

-- Average basket size overall
SELECT ROUND(AVG(item_count), 2) AS avg_basket_size
FROM (
    SELECT order_id, COUNT(*) AS item_count
    FROM fact_orders
    GROUP BY order_id
) basket_sizes;

-- Basket size distribution buckets
SELECT
    CASE
        WHEN item_count <= 5 THEN '1-5 items'
        WHEN item_count <= 10 THEN '6-10 items'
        WHEN item_count <= 20 THEN '11-20 items'
        ELSE '21+ items'
    END AS basket_size_bucket,
    COUNT(*) AS num_orders
FROM (
    SELECT order_id, COUNT(*) AS item_count
    FROM fact_orders
    GROUP BY order_id
) basket_sizes
GROUP BY basket_size_bucket
ORDER BY MIN(item_count);

-- Order timing pattern (volume by day-of-week and hour-of-day)
SELECT
    order_dow,
    order_hour_of_day,
    COUNT(DISTINCT order_id) AS order_count
FROM fact_orders
GROUP BY order_dow, order_hour_of_day
ORDER BY order_dow, order_hour_of_day;

-- Products frequently purchased together (simple co-occurrence, top pairs
-- within the same order — for a lightweight "frequently bought together" cut;
-- a full market-basket/association-rule analysis would use mlxtend in Python
-- if you want to go further, but is not required for the core deliverable)
SELECT
    a.product_name AS product_a,
    b.product_name AS product_b,
    COUNT(*) AS times_bought_together
FROM fact_orders a
JOIN fact_orders b
    ON a.order_id = b.order_id AND a.product_id < b.product_id
GROUP BY a.product_name, b.product_name
ORDER BY times_bought_together DESC
LIMIT 20;

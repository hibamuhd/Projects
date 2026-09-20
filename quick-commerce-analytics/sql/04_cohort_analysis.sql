-- 04_cohort_analysis.sql


WITH cohort_base AS (
    SELECT user_id, total_orders
    FROM dim_customer
),
cohort_size AS (
    SELECT COUNT(*) AS n FROM cohort_base
)
SELECT
    n.order_number,
    COUNT(cb.user_id) AS users_reaching,
    (SELECT n FROM cohort_size) AS cohort_size,
    ROUND(100.0 * COUNT(cb.user_id) / (SELECT n FROM cohort_size), 2) AS retention_pct
FROM (
    -- generate order_number sequence 1..20 (adapt to your SQL dialect;
    -- this pattern works in most engines with a recursive CTE or a numbers table)
    SELECT 1 AS order_number UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
    SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL
    SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL
    SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14 UNION ALL SELECT 15 UNION ALL
    SELECT 16 UNION ALL SELECT 17 UNION ALL SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20
) n
LEFT JOIN cohort_base cb ON cb.total_orders >= n.order_number
GROUP BY n.order_number
ORDER BY n.order_number;

-- Cohort size and one-time vs. multi-order split (for the cohort-size visual)
SELECT
    COUNT(*) AS cohort_size,
    SUM(CASE WHEN total_orders = 1 THEN 1 ELSE 0 END) AS one_time,
    SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) AS multi_order
FROM dim_customer;

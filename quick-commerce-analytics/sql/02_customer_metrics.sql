-- 02_customer_metrics.sql
-- Core customer KPIs: repeat rate, one-time rate, orders per customer.

-- Total / repeat / one-time customers
SELECT
    COUNT(*) AS total_customers,
    SUM(is_one_time_customer) AS one_time_customers,
    COUNT(*) - SUM(is_one_time_customer) AS repeat_customers,
    ROUND(100.0 * SUM(is_one_time_customer) / COUNT(*), 2) AS one_time_customer_pct,
    ROUND(100.0 * (COUNT(*) - SUM(is_one_time_customer)) / COUNT(*), 2) AS repeat_customer_rate_pct
FROM dim_customer;

-- Average / median orders per customer
SELECT
    ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
    MIN(total_orders) AS min_orders,
    MAX(total_orders) AS max_orders
FROM dim_customer;

-- Customer segment distribution (segments computed in 03_feature_engineering.py)
SELECT
    customer_segment,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM dim_customer), 2) AS pct_of_base,
    ROUND(AVG(total_orders), 2) AS avg_orders_in_segment
FROM dim_customer
GROUP BY customer_segment
ORDER BY avg_orders_in_segment DESC;

-- Distribution of days between orders (habitual purchase cadence)
SELECT
    ROUND(AVG(avg_days_between_orders), 2) AS avg_days_between_orders_overall
FROM dim_customer
WHERE avg_days_between_orders IS NOT NULL;

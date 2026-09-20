-- 06_delivery_analysis.sql

-- Overall delivery-time summary stats
SELECT
    ROUND(AVG(delivery_time_minutes), 2) AS avg_delivery_time,
    ROUND(AVG(CASE WHEN is_late = 1 THEN 100.0 ELSE 0 END), 2) AS late_delivery_rate_pct
FROM synthetic_delivery;

-- Median and percentiles (SQLite/Postgres syntax varies — this uses
-- percentile_cont, adapt to your engine, e.g. PERCENTILE_CONT in Postgres,
-- or compute in pandas if your SQL engine lacks window percentile support)
SELECT
    delivery_time_minutes
FROM synthetic_delivery
ORDER BY delivery_time_minutes
LIMIT 1
OFFSET (SELECT CAST(COUNT(*) * 0.5 AS INT) FROM synthetic_delivery); -- median (p50)

-- Delivery time by hour of day
SELECT
    o.order_hour_of_day,
    ROUND(AVG(sd.delivery_time_minutes), 2) AS avg_delivery_time,
    ROUND(100.0 * AVG(sd.is_late), 2) AS late_rate_pct
FROM synthetic_delivery sd
JOIN fact_orders o ON o.order_id = sd.order_id
GROUP BY o.order_hour_of_day
ORDER BY o.order_hour_of_day;

-- Delivery time by day of week
SELECT
    o.order_dow,
    ROUND(AVG(sd.delivery_time_minutes), 2) AS avg_delivery_time,
    ROUND(100.0 * AVG(sd.is_late), 2) AS late_rate_pct
FROM synthetic_delivery sd
JOIN fact_orders o ON o.order_id = sd.order_id
GROUP BY o.order_dow
ORDER BY o.order_dow;

-- Delivery time vs. customer segment (exploratory — is slower delivery
-- associated with lower-frequency segments? correlation only, not causal)
SELECT
    dc.customer_segment,
    ROUND(AVG(sd.delivery_time_minutes), 2) AS avg_delivery_time,
    ROUND(100.0 * AVG(sd.is_late), 2) AS late_rate_pct
FROM synthetic_delivery sd
JOIN fact_orders o ON o.order_id = sd.order_id
JOIN dim_customer dc ON dc.user_id = o.user_id
GROUP BY dc.customer_segment
ORDER BY avg_delivery_time DESC;

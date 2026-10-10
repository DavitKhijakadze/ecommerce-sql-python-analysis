SELECT
  COUNT(DISTINCT o.order_id) AS orders_count,
  ROUND(SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)), 2) AS revenue_gel
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status = 'Delivered';

SELECT
  strftime('%Y-%m', o.order_datetime) AS month,
  COUNT(DISTINCT o.order_id) AS orders_count,
  ROUND(SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)), 2) AS revenue_gel
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY month
ORDER BY month
LIMIT 6;

SELECT
  strftime('%Y-%m', o.order_datetime) AS month,
  ROUND(SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)), 2) AS revenue_gel,
  ROUND(SUM(oi.quantity * p.unit_cost_gel), 2) AS cost_gel,
  ROUND(SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) - SUM(oi.quantity * p.unit_cost_gel), 2) AS profit_gel,
  ROUND(100.0 * (SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) - SUM(oi.quantity * p.unit_cost_gel)) / SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)), 1) AS margin_pct
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'Delivered'
GROUP BY month
ORDER BY month
LIMIT 6;

SELECT COUNT(*) AS return_rows, COUNT(DISTINCT order_item_id) AS distinct_items, ROUND(SUM(refund_amount_gel),2) AS total_refund FROM returns

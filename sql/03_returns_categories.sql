WITH items AS (
  SELECT
    oi.order_item_id,
    p.category,
    oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0) AS revenue,
    oi.quantity * p.unit_cost_gel AS cost,
    COALESCE(r.refund_amount_gel, 0) AS refund,
    CASE WHEN r.return_id IS NULL THEN 0 ELSE 1 END AS is_returned
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
  WHERE o.status = 'Delivered'
)
SELECT
  ROUND(SUM(revenue), 2) AS revenue_gel,
  ROUND(SUM(refund), 2) AS refunds_gel,
  ROUND(SUM(revenue) - SUM(refund), 2) AS net_revenue_gel,
  ROUND(100.0 * SUM(refund) / SUM(revenue), 1) AS refund_pct
FROM items;

WITH items AS (
  SELECT
    oi.order_item_id,
    p.category,
    oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0) AS revenue,
    oi.quantity * p.unit_cost_gel AS cost,
    COALESCE(r.refund_amount_gel, 0) AS refund,
    CASE WHEN r.return_id IS NULL THEN 0 ELSE 1 END AS is_returned
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
  WHERE o.status = 'Delivered'
)
SELECT
  category,
  ROUND(SUM(revenue), 2) AS revenue_gel,
  ROUND(SUM(revenue) - SUM(cost), 2) AS profit_before_returns,
  ROUND(SUM(revenue) - SUM(cost) - SUM(refund), 2) AS profit_after_returns,
  ROUND(100.0 * (SUM(revenue) - SUM(cost) - SUM(refund)) / SUM(revenue), 1) AS margin_after_returns_pct,
  ROUND(100.0 * SUM(is_returned) / COUNT(*), 1) AS return_rate_pct
FROM items
GROUP BY category
ORDER BY profit_after_returns DESC;

SELECT
  reason,
  COUNT(*) AS returns_count,
  ROUND(SUM(refund_amount_gel), 2) AS refund_gel
FROM returns
GROUP BY reason
ORDER BY refund_gel DESC

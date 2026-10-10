-- 1. ფასდაკლების კოდები: ჩეკი, მარჟა, დაბრუნება
WITH order_totals AS (
  SELECT
    o.order_id,
    COALESCE(o.discount_code, 'NO CODE') AS code,
    SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) AS revenue,
    SUM(oi.quantity * p.unit_cost_gel) AS cost,
    SUM(COALESCE(r.refund_amount_gel, 0)) AS refund
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
  WHERE o.status = 'Delivered'
  GROUP BY o.order_id, code
)
SELECT
  code,
  COUNT(*) AS orders_count,
  ROUND(AVG(revenue), 2) AS avg_order_value,
  ROUND(100.0 * (SUM(revenue) - SUM(cost)) / SUM(revenue), 1) AS margin_pct,
  ROUND(100.0 * (SUM(revenue) - SUM(cost) - SUM(refund)) / SUM(revenue), 1) AS margin_after_returns_pct,
  ROUND(100.0 * SUM(refund) / SUM(revenue), 1) AS refund_pct
FROM order_totals
GROUP BY code
ORDER BY orders_count DESC;

-- 2. პროდუქტის დონეზე ფასდაკლების ზომა (discount_pct)
SELECT
  oi.discount_pct,
  COUNT(*) AS items_count,
  ROUND(SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)), 2) AS revenue_gel,
  ROUND(100.0 * (SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) - SUM(oi.quantity * p.unit_cost_gel))
        / SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)), 1) AS margin_pct
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'Delivered'
GROUP BY oi.discount_pct
ORDER BY oi.discount_pct;

-- 3. ფასდაკლების კოდი თვეების მიხედვით (როდის გამოიყენება)
SELECT
  strftime('%m', order_datetime) AS month_no,
  COALESCE(discount_code, 'NO CODE') AS code,
  COUNT(*) AS orders_count
FROM orders
WHERE status = 'Delivered' AND discount_code IN ('SUMMER15', 'BF25')
GROUP BY month_no, code
ORDER BY code, month_no;

-- 1. აქვისიციის არხები: რამდენი კლიენტი, რამდენმა იყიდა, რა შემოსავალი
WITH customer_sales AS (
  SELECT
    o.customer_id,
    COUNT(DISTINCT o.order_id) AS orders_count,
    SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status = 'Delivered'
  GROUP BY o.customer_id
)
SELECT
  c.acquisition_channel,
  COUNT(*) AS customers,
  COUNT(cs.customer_id) AS buyers,
  ROUND(100.0 * COUNT(cs.customer_id) / COUNT(*), 1) AS buyer_pct,
  ROUND(SUM(COALESCE(cs.revenue, 0)), 2) AS revenue_gel,
  ROUND(SUM(COALESCE(cs.revenue, 0)) / COUNT(*), 2) AS revenue_per_customer,
  ROUND(1.0 * SUM(COALESCE(cs.orders_count, 0)) / COUNT(cs.customer_id), 2) AS orders_per_buyer
FROM customers c
LEFT JOIN customer_sales cs ON cs.customer_id = c.customer_id
GROUP BY c.acquisition_channel
ORDER BY revenue_per_customer DESC;

-- 2. ქალაქები
WITH customer_sales AS (
  SELECT
    o.customer_id,
    SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status = 'Delivered'
  GROUP BY o.customer_id
)
SELECT
  c.city,
  COUNT(*) AS customers,
  ROUND(SUM(COALESCE(cs.revenue, 0)), 2) AS revenue_gel,
  ROUND(SUM(COALESCE(cs.revenue, 0)) / COUNT(*), 2) AS revenue_per_customer
FROM customers c
LEFT JOIN customer_sales cs ON cs.customer_id = c.customer_id
GROUP BY c.city
HAVING COUNT(*) >= 100
ORDER BY revenue_gel DESC;

-- 3. გამოწერა (newsletter) ზრდის შენაძენს?
WITH customer_sales AS (
  SELECT
    o.customer_id,
    SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  WHERE o.status = 'Delivered'
  GROUP BY o.customer_id
)
SELECT
  c.newsletter_subscribed,
  COUNT(*) AS customers,
  ROUND(100.0 * COUNT(cs.customer_id) / COUNT(*), 1) AS buyer_pct,
  ROUND(SUM(COALESCE(cs.revenue, 0)) / COUNT(*), 2) AS revenue_per_customer
FROM customers c
LEFT JOIN customer_sales cs ON cs.customer_id = c.customer_id
GROUP BY c.newsletter_subscribed;

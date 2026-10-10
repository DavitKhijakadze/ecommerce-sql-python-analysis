-- 1. რამდენჯერ ყიდულობს კლიენტი (მხოლოდ Delivered)
WITH per_customer AS (
  SELECT customer_id, COUNT(*) AS orders_count
  FROM orders
  WHERE status = 'Delivered'
  GROUP BY customer_id
)
SELECT
  orders_count,
  COUNT(*) AS customers,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM per_customer), 1) AS pct_of_buyers
FROM per_customer
GROUP BY orders_count
ORDER BY orders_count;

-- 2. რამდენ დღეში ბრუნდება კლიენტი (Window functions: ROW_NUMBER, LAG)
WITH ordered AS (
  SELECT
    customer_id,
    order_datetime,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_datetime) AS order_no,
    LAG(order_datetime) OVER (PARTITION BY customer_id ORDER BY order_datetime) AS prev_order
  FROM orders
  WHERE status = 'Delivered'
)
SELECT
  order_no,
  COUNT(*) AS orders_count,
  ROUND(AVG(julianday(order_datetime) - julianday(prev_order)), 1) AS avg_days_since_prev
FROM ordered
WHERE order_no BETWEEN 2 AND 5
GROUP BY order_no
ORDER BY order_no;

-- 3. შემოსავლის რა წილი მოდის განმეორებით შეკვეთებზე წლების მიხედვით
WITH ordered AS (
  SELECT
    o.order_id,
    o.order_datetime,
    ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_datetime) AS order_no
  FROM orders o
  WHERE o.status = 'Delivered'
),
order_revenue AS (
  SELECT order_id, SUM(quantity * unit_price_gel * (1 - discount_pct / 100.0)) AS revenue
  FROM order_items
  GROUP BY order_id
)
SELECT
  strftime('%Y', od.order_datetime) AS year,
  ROUND(SUM(CASE WHEN od.order_no = 1 THEN orv.revenue ELSE 0 END), 2) AS first_order_revenue,
  ROUND(SUM(CASE WHEN od.order_no > 1 THEN orv.revenue ELSE 0 END), 2) AS repeat_order_revenue,
  ROUND(100.0 * SUM(CASE WHEN od.order_no > 1 THEN orv.revenue ELSE 0 END) / SUM(orv.revenue), 1) AS repeat_share_pct
FROM ordered od
JOIN order_revenue orv ON orv.order_id = od.order_id
GROUP BY year
ORDER BY year;

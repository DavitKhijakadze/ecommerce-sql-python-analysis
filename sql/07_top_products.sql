-- 1. TOP 10 პროდუქტი მოგებით (დაბრუნებების შემდეგ), product_id-ით
WITH items AS (
  SELECT
    p.product_id, p.product_name, p.category,
    oi.quantity,
    oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0) AS revenue,
    oi.quantity * p.unit_cost_gel AS cost,
    COALESCE(r.refund_amount_gel, 0) AS refund
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
  WHERE o.status = 'Delivered'
)
SELECT
  product_id, product_name, category,
  SUM(quantity) AS units,
  ROUND(SUM(revenue), 2) AS revenue_gel,
  ROUND(SUM(revenue) - SUM(cost) - SUM(refund), 2) AS profit_gel
FROM items
GROUP BY product_id, product_name, category
ORDER BY profit_gel DESC
LIMIT 10;

-- 2. საუკეთესო 2 პროდუქტი თითო კატეგორიაში (Window function: RANK)
WITH items AS (
  SELECT
    p.product_id, p.product_name, p.category,
    oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0) AS revenue,
    oi.quantity * p.unit_cost_gel AS cost,
    COALESCE(r.refund_amount_gel, 0) AS refund
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
  WHERE o.status = 'Delivered'
),
product_profit AS (
  SELECT
    product_id, product_name, category,
    ROUND(SUM(revenue) - SUM(cost) - SUM(refund), 2) AS profit_gel
  FROM items
  GROUP BY product_id, product_name, category
),
ranked AS (
  SELECT *,
    RANK() OVER (PARTITION BY category ORDER BY profit_gel DESC) AS rank_in_category
  FROM product_profit
)
SELECT category, rank_in_category, product_id, product_name, profit_gel
FROM ranked
WHERE rank_in_category <= 2
ORDER BY category, rank_in_category;

-- 3. "ბალასტი": 10 პროდუქტი ყველაზე მცირე მოგებით
WITH items AS (
  SELECT
    p.product_id, p.product_name, p.category,
    oi.quantity,
    oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0) AS revenue,
    oi.quantity * p.unit_cost_gel AS cost,
    COALESCE(r.refund_amount_gel, 0) AS refund
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  JOIN products p ON p.product_id = oi.product_id
  LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
  WHERE o.status = 'Delivered'
)
SELECT
  product_id, product_name, category,
  SUM(quantity) AS units,
  ROUND(SUM(revenue) - SUM(cost) - SUM(refund), 2) AS profit_gel
FROM items
GROUP BY product_id, product_name, category
ORDER BY profit_gel ASC
LIMIT 10;

-- 4. პროდუქტები, რომლებიც არასოდეს გაყიდულა (Delivered)
SELECT p.product_id, p.product_name, p.category
FROM products p
WHERE p.product_id NOT IN (
  SELECT oi.product_id
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  WHERE o.status = 'Delivered'
);

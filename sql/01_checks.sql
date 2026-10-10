SELECT 'customers' AS table_name, COUNT(*) AS rows_count FROM customers
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'returns', COUNT(*) FROM returns;

SELECT status, COUNT(*) AS orders_count FROM orders GROUP BY status ORDER BY orders_count DESC;

SELECT COUNT(*) AS duplicate_order_ids FROM (SELECT order_id FROM orders GROUP BY order_id HAVING COUNT(*) > 1);

SELECT COUNT(*) AS items_without_order FROM order_items WHERE order_id NOT IN (SELECT order_id FROM orders);

SELECT COUNT(*) AS orders_without_customer FROM orders WHERE customer_id NOT IN (SELECT customer_id FROM customers);

SELECT
  SUM(CASE WHEN discount_code IS NULL OR discount_code = '' THEN 1 ELSE 0 END) AS no_discount_code,
  SUM(CASE WHEN delivery_date IS NULL OR delivery_date = '' THEN 1 ELSE 0 END) AS no_delivery_date
FROM orders;

SELECT MIN(order_datetime) AS first_order, MAX(order_datetime) AS last_order FROM orders;

SELECT product_name, COUNT(*) AS ids_count FROM products GROUP BY product_name HAVING COUNT(*) > 1 ORDER BY ids_count DESC;

SELECT COUNT(*) AS price_differs_from_catalog
FROM order_items oi JOIN products p ON p.product_id = oi.product_id
WHERE oi.unit_price_gel <> p.unit_price_gel;

SELECT COUNT(*) AS returns_without_item FROM returns WHERE order_item_id NOT IN (SELECT order_item_id FROM order_items)

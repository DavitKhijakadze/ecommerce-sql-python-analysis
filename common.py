import sqlite3
import pandas as pd

DB_PATH = "ecommerce.db"


def run_query(sql):
    """SQL მოთხოვნას უშვებს ბაზაზე და შედეგს pandas ცხრილად აბრუნებს."""
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, con)
    con.close()
    return df


def load_items():
    """თითო სტრიქონი = ერთი პროდუქტი შეკვეთაში (მხოლოდ Delivered)."""
    sql = """
    SELECT
        oi.order_item_id,
        oi.order_id,
        o.customer_id,
        o.order_datetime,
        p.product_id,
        p.product_name,
        p.category,
        oi.quantity,
        oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0) AS revenue,
        oi.quantity * p.unit_cost_gel AS cost,
        COALESCE(r.refund_amount_gel, 0) AS refund
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
    WHERE o.status = 'Delivered'
    """
    df = run_query(sql)
    df["order_datetime"] = pd.to_datetime(df["order_datetime"])
    df["order_month"] = df["order_datetime"].dt.to_period("M")
    df["profit"] = df["revenue"] - df["cost"] - df["refund"]
    return df

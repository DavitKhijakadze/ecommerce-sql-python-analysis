import numpy as np
import pandas as pd
from common import load_items

items = load_items()
items["net"] = items["revenue"] - items["refund"]

# "დღევანდელი" თარიღი = ბოლო შეკვეთის მეორე დღე
snapshot = items["order_datetime"].max() + pd.Timedelta(days=1)

# თითო კლიენტზე: ბოლო შეკვეთა, შეკვეთების რაოდენობა, სუფთა დახარჯული თანხა
rfm = items.groupby("customer_id").agg(
    last_order=("order_datetime", "max"),
    frequency=("order_id", "nunique"),
    monetary=("net", "sum"),
).reset_index()
rfm["recency_days"] = (snapshot - rfm["last_order"]).dt.days

# სეგმენტები: წესები ზემოდან ქვემოთ მოწმდება
conditions = [
    (rfm["frequency"] >= 3) & (rfm["recency_days"] <= 180),
    (rfm["frequency"] == 2) & (rfm["recency_days"] <= 180),
    (rfm["frequency"] >= 2) & (rfm["recency_days"] > 180),
    (rfm["frequency"] == 1) & (rfm["recency_days"] <= 90),
    (rfm["frequency"] == 1) & (rfm["recency_days"] <= 365),
]
names = ["Champions", "Loyal", "At risk", "New", "One-time, cooling"]
rfm["segment"] = np.select(conditions, names, default="One-time, lost")

summary = rfm.groupby("segment").agg(
    customers=("customer_id", "count"),
    revenue=("monetary", "sum"),
    avg_revenue=("monetary", "mean"),
    avg_recency_days=("recency_days", "mean"),
)
summary["customers_pct"] = 100 * summary["customers"] / summary["customers"].sum()
summary["revenue_pct"] = 100 * summary["revenue"] / summary["revenue"].sum()
summary = summary.sort_values("revenue", ascending=False).round(1)

print(summary)
rfm.to_csv("rfm_segments.csv", index=False)
print("შენახულია: rfm_segments.csv")

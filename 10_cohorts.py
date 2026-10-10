import pandas as pd
from common import load_items

items = load_items()

# ერთი სტრიქონი = ერთი შეკვეთა
orders = items.groupby(["order_id", "customer_id"], as_index=False)["order_datetime"].first()
orders["order_month"] = orders["order_datetime"].dt.to_period("M")

# კოჰორტა = თვე, როცა კლიენტმა პირველად იყიდა
cohort = orders.groupby("customer_id")["order_month"].min().rename("cohort_month")
orders = orders.join(cohort, on="customer_id")

# რამდენი თვე გავიდა პირველი შეკვეთიდან
orders["months_since"] = (
    (orders["order_month"].dt.year - orders["cohort_month"].dt.year) * 12
    + (orders["order_month"].dt.month - orders["cohort_month"].dt.month)
)

# რამდენი უნიკალური კლიენტი იყო აქტიური თითო თვეს თითო კოჰორტაში
counts = (
    orders.groupby(["cohort_month", "months_since"])["customer_id"]
    .nunique()
    .unstack(fill_value=0)
)

# მომავალი თვეები (რომლებიც მონაცემში ჯერ არ არის) ცარიელი უნდა იყოს
last = orders["order_month"].max()
for cohort_month in counts.index:
    max_offset = (last.year - cohort_month.year) * 12 + (last.month - cohort_month.month)
    counts.loc[cohort_month, counts.columns > max_offset] = float("nan")

# პროცენტი = აქტიური / კოჰორტის ზომა
retention = counts.div(counts[0], axis=0) * 100

print("კოჰორტის ზომა (პირველი 5):")
print(counts[0].head())
print()
print("საშუალო retention % თვეების მიხედვით (0 = პირველი შეკვეთის თვე):")
print(retention.mean().round(1).head(13))

retention.round(1).to_csv("cohort_retention.csv")
counts[0].to_csv("cohort_sizes.csv", header=["customers"])
print("შენახულია: cohort_retention.csv")

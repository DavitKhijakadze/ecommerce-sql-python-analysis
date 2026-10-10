from common import run_query, load_items

# 1. ყველა ცხრილის სწრაფი დათვალიერება
for table in ["customers", "orders", "order_items", "products", "returns"]:
    df = run_query(f"SELECT * FROM {table}")
    print("=" * 60)
    print(table, "- ზომა (სტრიქონი, სვეტი):", df.shape)
    print(df.head(3))
    print("ცარიელი უჯრები სვეტების მიხედვით:")
    print(df.isna().sum())

# 2. ჩვენი მთავარი ცხრილი: თითო პროდუქტი შეკვეთაში
items = load_items()
print("=" * 60)
print("items ზომა:", items.shape)
print(items.head())
print(items[["revenue", "cost", "refund", "profit"]].describe().round(2))

# 3. შემოწმება: SQL-ის შედეგს უნდა დაემთხვეს (1950699.88)
print("=" * 60)
print("ჯამური შემოსავალი:", round(items["revenue"].sum(), 2))

monthly = items.groupby("order_month")[["revenue", "profit"]].sum().round(2)
print(monthly.head())
print(monthly.tail())

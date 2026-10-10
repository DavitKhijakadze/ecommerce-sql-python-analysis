import sqlite3, sys
import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
con = sqlite3.connect("ecommerce.db")

for query in text.split(";"):
    query = query.strip()
    if not query:
        continue
    print("-" * 60)
    print(query)
    print()
    print(pd.read_sql_query(query, con).to_string(index=False))
    print()
con.close()

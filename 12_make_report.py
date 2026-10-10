import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from common import load_items, run_query

INK = "#0b0b0b"
MUTED = "#52514e"
BLUE = "#2a78d6"
SURFACE = "#fcfcfb"

items = load_items()

# ---------- ციფრები, რომლებიც ანგარიშში მოხვდება ----------
revenue = items["revenue"].sum()
refund = items["refund"].sum()
profit = items["profit"].sum()
orders = items["order_id"].nunique()
buyers = items["customer_id"].nunique()

per_buyer = items.groupby("customer_id")["order_id"].nunique()
one_time_pct = 100 * (per_buyer == 1).mean()

cat = items.groupby("category").agg(revenue=("revenue", "sum"), profit=("profit", "sum"),
                                    sold=("order_item_id", "count"))
cat["return_rate"] = 100 * items[items["refund"] > 0].groupby("category")["order_item_id"].count() / cat["sold"]
cat["margin"] = 100 * cat["profit"] / cat["revenue"]
worst_cat = cat["margin"].idxmin()
rr_sorted = cat["return_rate"].sort_values(ascending=False)

wrong_size = run_query("""
    SELECT p.category, COUNT(*) AS n FROM returns r
    JOIN order_items oi ON oi.order_item_id = r.order_item_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE r.reason = 'Wrong size' GROUP BY p.category""")

customers = run_query("SELECT customer_id, acquisition_channel FROM customers")
customers["revenue"] = customers["customer_id"].map(items.groupby("customer_id")["revenue"].sum()).fillna(0)
ch = customers.groupby("acquisition_channel")["revenue"].mean().sort_values()

codes = run_query("""
    SELECT COALESCE(o.discount_code, 'NO CODE') AS code,
           100.0 * (SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) - SUM(oi.quantity * p.unit_cost_gel)
                    - SUM(COALESCE(r.refund_amount_gel, 0)))
           / SUM(oi.quantity * oi.unit_price_gel * (1 - oi.discount_pct / 100.0)) AS margin
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN returns r ON r.order_item_id = oi.order_item_id
    WHERE o.status = 'Delivered' GROUP BY code""").set_index("code")["margin"]

gaps = run_query("""
    WITH ordered AS (
      SELECT julianday(order_datetime) - julianday(LAG(order_datetime) OVER
             (PARTITION BY customer_id ORDER BY order_datetime)) AS gap
      FROM orders WHERE status = 'Delivered')
    SELECT AVG(gap) AS avg_gap FROM ordered""")["avg_gap"].iloc[0]

prod = items.groupby(["product_id", "product_name"])["profit"].sum().sort_values()
loss_id, loss_name = prod.index[0]

kpis = [
    ("Net revenue", f"{revenue - refund:,.0f} GEL"),
    ("Profit after returns", f"{profit:,.0f} GEL"),
    ("Delivered orders", f"{orders:,}"),
    ("Buying customers", f"{buyers:,}"),
]

recommendations = [
    f"{worst_cat}: return rate {cat.loc[worst_cat, 'return_rate']:.1f}% (next highest: {rr_sorted.iloc[1]:.1f}%), "
    f"margin after returns {cat.loc[worst_cat, 'margin']:.1f}%. All {int(wrong_size['n'].sum())} 'Wrong size' returns are in "
    f"{', '.join(wrong_size['category'])}. Add size guides and fit notes before adding more stock.",
    f"Acquisition: customers from {ch.index[0]} bring {ch.iloc[0]:,.0f} GEL on average vs {ch.iloc[-1]:,.0f} GEL from "
    f"{ch.index[-1]}. Shift part of the ads budget toward referral and email.",
    f"Discounts: BF25 and SUMMER15 earn {codes['BF25']:.1f}% and {codes['SUMMER15']:.1f}% margin after returns, "
    f"against {codes['NO CODE']:.1f}% for orders without a code. Cap the depth of these campaigns.",
    f"Retention: {one_time_pct:.0f}% of buyers purchase only once, and repeat orders come about {gaps:.0f} days apart. "
    f"A reminder email around day {gaps - 7:.0f} after each order is the first test to run.",
    f"Assortment: {loss_name} ({loss_id}) lost money after returns ({prod.iloc[0]:,.0f} GEL). Review its price, cost and returns.",
]

# ---------- PDF ----------
A4 = (8.27, 11.69)


def new_page(pdf, title):
    fig = plt.figure(figsize=A4, facecolor=SURFACE)
    fig.text(0.07, 0.955, title, fontsize=18, fontweight="bold", color=INK, ha="left", va="top")
    return fig


def add_image(fig, path, top, height):
    img = plt.imread(path)
    ax = fig.add_axes([0.04, top - height, 0.92, height])
    ax.imshow(img)
    ax.axis("off")


with PdfPages("report.pdf") as pdf:
    # 1 გვერდი: შეჯამება
    fig = new_page(pdf, "E-commerce analysis: where the profit comes from")
    fig.text(0.07, 0.915, "Georgian online store, Jan 2024 - Sep 2026. Synthetic dataset. Delivered orders only; "
             "profit is after product cost and refunds.", fontsize=10.5, color=MUTED, ha="left", va="top", wrap=True)
    for i, (label, value) in enumerate(kpis):
        x = 0.07 + i * 0.225
        fig.text(x, 0.835, value, fontsize=15, fontweight="bold", color=BLUE, ha="left")
        fig.text(x, 0.812, label, fontsize=9.5, color=MUTED, ha="left")
    fig.text(0.07, 0.755, "What to do next", fontsize=14, fontweight="bold", color=INK, ha="left")
    y = 0.725
    for n, text in enumerate(recommendations, 1):
        lines = textwrap.wrap(text, 92)
        fig.text(0.07, y, f"{n}.", fontsize=10.5, fontweight="bold", color=INK, ha="left", va="top")
        fig.text(0.10, y, "\n".join(lines), fontsize=10.5, color=INK, ha="left", va="top", linespacing=1.45)
        y -= 0.022 * len(lines) + 0.022
    fig.text(0.07, 0.04, "Tools: SQL (SQLite), Python (pandas, matplotlib). Full code in the project repository.",
             fontsize=9, color=MUTED, ha="left")
    pdf.savefig(fig)
    plt.close(fig)

    # 2-4 გვერდები: გრაფიკები, ორ-ორი
    pairs = [
        ("Growth and profitability", "01_monthly_revenue_profit.png", "02_margin_by_category.png"),
        ("Returns and customers", "03_return_rate_by_category.png", "04_revenue_per_customer_by_channel.png"),
        ("Loyalty", "05_revenue_share_by_segment.png", "06_cohort_retention.png"),
    ]
    for title, a, b in pairs:
        fig = new_page(pdf, title)
        add_image(fig, f"charts/{a}", 0.91, 0.43)
        add_image(fig, f"charts/{b}", 0.47, 0.43)
        pdf.savefig(fig)
        plt.close(fig)

print("შენახულია: report.pdf")
print()
for r in recommendations:
    print("-", r)

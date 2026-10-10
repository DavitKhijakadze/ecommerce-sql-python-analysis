import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from common import load_items, run_query

os.makedirs("charts", exist_ok=True)

# ფერები: ერთი მთავარი (ლურჯი) და ერთი აქცენტი (ნარინჯისფერი) იმ ერთ რამეზე, რაც გვინდა გამოვაჩინოთ
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"
ORANGE = "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "font.size": 11,
})


def finish(fig, ax, title, subtitle, filename):
    """სათაური, ქვესათაური და შენახვა."""
    fig.text(0.06, 0.95, title, fontsize=15, fontweight="bold", ha="left", va="top")
    fig.text(0.06, 0.885, subtitle, fontsize=11, color=MUTED, ha="left", va="top")
    fig.subplots_adjust(top=0.80, left=0.20, right=0.94, bottom=0.12)
    fig.savefig(f"charts/{filename}", dpi=200)
    plt.close(fig)
    print("შენახულია: charts/" + filename)


def hbar(labels, values, highlight, title, subtitle, filename, fmt, xlabel=""):
    """ჰორიზონტალური სვეტოვანი გრაფიკი, ერთი სვეტი გამოყოფილია."""
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [ORANGE if l == highlight else BLUE for l in labels]
    ax.barh(labels, values, color=colors, height=0.55)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.01, i, fmt(v), va="center", fontsize=10, color=INK)
    ax.set_xlim(0, max(values) * 1.15)
    ax.set_xlabel(xlabel)
    finish(fig, ax, title, subtitle, filename)


items = load_items()

# ---------- 1. თვიური შემოსავალი და მოგება ----------
monthly = items.groupby("order_month")[["revenue", "profit"]].sum()
x = monthly.index.to_timestamp()
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(x, monthly["revenue"], color=BLUE, linewidth=2)
ax.plot(x, monthly["profit"], color=ORANGE, linewidth=2)
ax.text(x[-1], monthly["revenue"].iloc[-1], "  Revenue", color=INK, va="center")
ax.text(x[-1], monthly["profit"].iloc[-1], "  Profit", color=INK, va="center")
ax.set_ylim(0)
ax.yaxis.set_major_formatter(lambda v, p: f"{v:,.0f}")
ax.set_ylabel("GEL")
rev_growth = 100 * (monthly["revenue"].iloc[-12:].sum() / monthly["revenue"].iloc[:12].sum() - 1)
profit_growth = 100 * (monthly["profit"].iloc[-12:].sum() / monthly["profit"].iloc[:12].sum() - 1)
finish(fig, ax, "Revenue and profit have both nearly doubled",
       f"Last 12 months vs first 12 months: revenue +{rev_growth:.0f}%, profit +{profit_growth:.0f}%. Delivered orders, profit after returns.",
       "01_monthly_revenue_profit.png")

# ---------- 2-3. კატეგორიები ----------
cat = items.groupby("category").agg(
    revenue=("revenue", "sum"), profit=("profit", "sum"), refund=("refund", "sum"),
    sold=("order_item_id", "count"),
)
returned = items[items["refund"] > 0].groupby("category")["order_item_id"].count()
cat["return_rate"] = 100 * returned / cat["sold"]
cat["margin"] = 100 * cat["profit"] / cat["revenue"]

c2 = cat.sort_values("margin", ascending=False)
worst = c2["margin"].idxmin()
hbar(list(c2.index), list(c2["margin"]), worst,
     f"{worst} keeps the least profit per lari of revenue",
     "Profit margin after returns, by category",
     "02_margin_by_category.png", lambda v: f"{v:.1f}%")

c3 = cat.sort_values("return_rate", ascending=False)
top = c3["return_rate"].idxmax()
second = c3["return_rate"].sort_values(ascending=False).iloc[1]
ratio = c3["return_rate"].max() / second
hbar(list(c3.index), list(c3["return_rate"]), top,
     f"{top} returns are {ratio:.1f}x the next-highest category",
     "Share of items sold that were returned",
     "03_return_rate_by_category.png", lambda v: f"{v:.1f}%")

# ---------- 4. არხები ----------
customers = run_query("SELECT customer_id, acquisition_channel FROM customers")
per_customer = items.groupby("customer_id")["revenue"].sum()
customers["revenue"] = customers["customer_id"].map(per_customer).fillna(0)
ch = customers.groupby("acquisition_channel")["revenue"].mean().sort_values(ascending=False)
low = ch.idxmin()
hbar(list(ch.index), list(ch.values), low,
     f"Customers from {low} spend the least",
     "Average revenue per acquired customer, GEL (delivered orders)",
     "04_revenue_per_customer_by_channel.png", lambda v: f"{v:,.0f}")

# ---------- 5. RFM სეგმენტები ----------
rfm = pd.read_csv("rfm_segments.csv")
seg = rfm.groupby("segment")["monetary"].sum().sort_values(ascending=False)
share = 100 * seg / seg.sum()
hbar(list(share.index), list(share.values), "At risk",
     f"'At risk' customers hold {share['At risk']:.0f}% of revenue",
     "Share of net revenue by customer segment (2+ orders, last purchase over 180 days ago = At risk)",
     "05_revenue_share_by_segment.png", lambda v: f"{v:.1f}%")

# ---------- 6. Cohort retention heatmap ----------
ret = pd.read_csv("cohort_retention.csv", index_col=0)
ret = ret[[str(i) for i in range(1, 13)]]
fig, ax = plt.subplots(figsize=(9, 6.5))
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("blues", ["#cde2fb", "#2a78d6", "#0d366b"])
img = ax.imshow(ret.values, cmap=cmap, aspect="auto", vmin=0, vmax=np.nanmax(ret.values))
ax.grid(False)
ax.set_xticks(range(12))
ax.set_xticklabels(range(1, 13))
step = 3
ax.set_yticks(range(0, len(ret), step))
ax.set_yticklabels(ret.index[::step])
ax.set_xlabel("Months since first order")
cbar = fig.colorbar(img, ax=ax)
cbar.set_label("% of cohort active")
cbar.outline.set_visible(False)
avg1 = ret["1"].mean()
finish(fig, ax, "Fewer than 1 in 5 new customers buys again the next month",
       f"Monthly cohort retention. Average month-1 retention is {avg1:.0f}% and fades steadily after that.",
       "06_cohort_retention.png")

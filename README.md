# E-commerce Sales Analysis (SQL + Python)

Analysis of a Georgian online store's orders, customers, products and returns
(Jan 2024 - Sep 2026). The dataset is synthetic and created for demonstration.

## Business questions
- Where does the profit come from, and where is it lost?
- Which acquisition channels bring the most valuable customers?
- Do customers come back? Do discounts pay off?

## Key findings
- Revenue and profit nearly doubled (last 12 months vs first 12 months: +90% / +91%).
- Fashion returns 13.0% of items sold (next highest: 7.6%); all "Wrong size" returns are in Fashion.
  Margin after returns is 19.1% vs 25-30% elsewhere.
- Instagram/Facebook Ads bring the most customers but the lowest revenue per customer (296 GEL vs 380 GEL for Referral).
- BF25 and SUMMER15 discount codes earn 8.5% and 16.1% margin after returns vs 27.5% without a code.
- 56% of buyers purchase only once; repeat orders come about 52 days apart.
- "At risk" customers (2+ orders, inactive 180+ days) hold 47% of net revenue.

## Project structure
sql/            SQL queries (data checks, revenue, returns, channels, retention, discounts, products)
common.py       shared helpers
08-12_*.py      Python analysis (RFM, cohorts, charts, PDF report)
charts/         generated charts
report.pdf      summary report

## How to run
pip install pandas matplotlib
python run_sql.py sql/02_revenue.sql
python 09_rfm_segments.py
python 10_cohorts.py
python 11_charts.py
python 12_make_report.py

## Skills shown
SQL: JOINs, CTEs, window functions (ROW_NUMBER, LAG, RANK), aggregation
Python: pandas, cohort and RFM analysis, matplotlib
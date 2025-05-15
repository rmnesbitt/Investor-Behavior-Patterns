import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "../data")
CHART_DIR = os.path.join(BASE_DIR, "../charts")
os.makedirs(CHART_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "investor_behavior.db")
connection = sqlite3.connect(DB_PATH)

def save_plot(fig, filename):
    fig_path = os.path.join(CHART_DIR, filename)
    fig.savefig(fig_path, bbox_inches='tight')
    plt.close(fig)

# Load data
products_by_month = pd.read_sql_query("""
SELECT 
    strftime('%Y-%m', txn_date) AS month, 
    product_id, 
    COUNT(*) AS txn_count, 
    SUM(amount) AS total_amount
FROM p1_transactions
GROUP BY month, product_id
ORDER BY month;
""", connection)

product_txn_volume = pd.read_sql_query("""
SELECT 
    pr.name AS product_name, 
    pr.category, 
    COUNT(*) AS txn_count
FROM p1_transactions t
JOIN p1_products pr ON t.product_id = pr.product_id
GROUP BY pr.product_id
ORDER BY txn_count DESC;
""", connection)

product_fin_volume = pd.read_sql_query("""
SELECT 
    pr.name AS product_name, 
    pr.category, 
    SUM(t.amount) AS total_amount
FROM p1_transactions t
JOIN p1_products pr ON t.product_id = pr.product_id
GROUP BY pr.product_id
ORDER BY total_amount DESC;
""", connection)

portfolio_vs_product = pd.read_sql_query("""
SELECT 
    pr.category, 
    ROUND(AVG(p.total_value), 2) AS avg_portfolio_value
FROM p1_transactions t
JOIN p1_products pr ON t.product_id = pr.product_id
JOIN p1_accounts a ON t.account_id = a.account_id
JOIN p1_portfolios p ON a.account_id = p.account_id
GROUP BY pr.category;
""", connection)

txn_volume_by_risk = pd.read_sql_query("""
SELECT 
    a.risk_profile, 
    COUNT(t.txn_id) AS txn_count
FROM p1_accounts a
JOIN p1_transactions t ON a.account_id = t.account_id
GROUP BY a.risk_profile;
""", connection)

risk_vs_value = pd.read_sql_query("""
SELECT 
    a.risk_profile, 
    ROUND(AVG(p.total_value), 2) AS avg_value
FROM p1_accounts a
JOIN p1_portfolios p ON a.account_id = p.account_id
GROUP BY a.risk_profile;
""", connection)

# Charts
# 1. Monthly Transactions
monthly_txn = products_by_month.groupby(['month'])['txn_count'].sum().reset_index()
fig1, ax1 = plt.subplots()
ax1.plot(monthly_txn['month'], monthly_txn['txn_count'], marker='o')
ax1.set_title("Total Transactions per Month")
ax1.set_xlabel("Month")
ax1.set_ylabel("Transaction Count")
ax1.tick_params(axis='x', rotation=45)
save_plot(fig1, "monthly_transaction_volume.png")

# 2. Top Products by Volume
fig2, ax2 = plt.subplots()
top_txn_products = product_txn_volume.head(10)
ax2.bar(top_txn_products['product_name'], top_txn_products['txn_count'])
ax2.set_title("Top Products by Transaction Volume")
ax2.set_ylabel("Transaction Count")
ax2.tick_params(axis='x', rotation=45)
save_plot(fig2, "top_products_by_volume.png")

# 3. Top Products by Financial Volume
fig3, ax3 = plt.subplots()
top_fin_products = product_fin_volume.head(10)
ax3.bar(top_fin_products['product_name'], top_fin_products['total_amount'])
ax3.set_title("Top Products by Financial Volume")
ax3.set_ylabel("Total Amount")
ax3.tick_params(axis='x', rotation=45)
save_plot(fig3, "top_products_by_financial_volume.png")

# 4. Avg Portfolio by Product Category
fig4, ax4 = plt.subplots()
ax4.bar(portfolio_vs_product['category'], portfolio_vs_product['avg_portfolio_value'])
ax4.set_title("Average Portfolio Value by Product Category")
ax4.set_ylabel("Avg Portfolio Value")
ax4.tick_params(axis='x', rotation=45)
save_plot(fig4, "portfolio_value_by_product_category.png")

# 5. Risk Profile vs Transaction Volume
fig5, ax5 = plt.subplots()
ax5.bar(txn_volume_by_risk['risk_profile'], txn_volume_by_risk['txn_count'])
ax5.set_title("Transaction Volume by Risk Profile")
ax5.set_ylabel("Transaction Count")
save_plot(fig5, "txn_volume_by_risk_profile.png")

# 6. Risk Profile vs Portfolio Value
fig6, ax6 = plt.subplots()
ax6.bar(risk_vs_value['risk_profile'], risk_vs_value['avg_value'])
ax6.set_title("Portfolio Value by Risk Profile")
ax6.set_ylabel("Average Portfolio Value")
save_plot(fig6, "portfolio_value_by_risk_profile.png")

connection.close()

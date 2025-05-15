import sqlite3
import pandas as pd
import os

DB_PATH = "../data/investor_behavior.db"
connection = sqlite3.connect(DB_PATH)

# Output directory
OUTDIR = "../data"
os.makedirs(OUTDIR, exist_ok=True)

# New questions and queries
queries = {
    "fee_efficiency_by_product": """
        SELECT 
            pr.name AS product_name,
            pr.category,
            ROUND(SUM(t.amount * pr.fee_pct / 100.0), 2) AS total_fees,
            ROUND(SUM(t.amount), 2) AS total_volume,
            ROUND(SUM(t.amount * pr.fee_pct / 100.0) / SUM(t.amount), 4) AS fee_per_dollar
        FROM p1_transactions t
        JOIN p1_products pr ON t.product_id = pr.product_id
        GROUP BY pr.product_id
        ORDER BY fee_per_dollar DESC;
    """,
    "portfolio_vs_account_age": """
        SELECT 
            a.account_id,
            ROUND(JULIANDAY('now') - JULIANDAY(u.signup_date)) AS account_age_days,
            p.total_value
        FROM p1_accounts a
        JOIN p1_users u ON a.user_id = u.user_id
        JOIN p1_portfolios p ON a.account_id = p.account_id;
    """,
    "region_vs_product_preference": """
        SELECT 
            u.region,
            pr.category,
            COUNT(*) AS txn_count,
            ROUND(SUM(t.amount), 2) AS total_invested
        FROM p1_transactions t
        JOIN p1_accounts a ON t.account_id = a.account_id
        JOIN p1_users u ON a.user_id = u.user_id
        JOIN p1_products pr ON t.product_id = pr.product_id
        GROUP BY u.region, pr.category
        ORDER BY u.region, total_invested DESC;
    """,
    "risk_vs_fee_load": """
        SELECT 
            a.risk_profile,
            ROUND(SUM(t.amount * pr.fee_pct / 100.0) / COUNT(t.txn_id), 2) AS avg_fee_per_txn
        FROM p1_transactions t
        JOIN p1_products pr ON t.product_id = pr.product_id
        JOIN p1_accounts a ON t.account_id = a.account_id
        GROUP BY a.risk_profile;
    """,
    "user_account_summary": """
        SELECT 
            u.user_id,
            COUNT(DISTINCT a.account_id) AS num_accounts,
            COUNT(t.txn_id) AS txn_count,
            ROUND(SUM(t.amount), 2) AS total_txn_amount,
            ROUND(AVG(p.total_value), 2) AS avg_portfolio_value
        FROM p1_users u
        JOIN p1_accounts a ON u.user_id = a.user_id
        LEFT JOIN p1_transactions t ON a.account_id = t.account_id
        LEFT JOIN p1_portfolios p ON a.account_id = p.account_id
        GROUP BY u.user_id;
    """
}

# Execute and save
for name, query in queries.items():
    df = pd.read_sql_query(query, connection)
    df.to_csv(f"{OUTDIR}/{name}.csv", index=False)

connection.close()
